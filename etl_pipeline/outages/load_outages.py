"""
Load outage data into RDS.
Lambda handler: load_outages.handler
"""

from __future__ import annotations

import json
from os import environ as ENV
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd
from psycopg2 import connect
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from transform_outages import transform_outages
from extract_outages_csv import generate_outage_csv


def get_db_connection():
    """Connect to the Postgres database on RDS using env vars."""
    load_dotenv()

    return connect(
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        sslmode=ENV.get("DB_SSLMODE", "require"),  # RDS defaults
    )


def sql_upsert_outage() -> str:
    """ Upsert outages by outage_id; inserts new rows or updates start_time, etr, category_id, and status on conflict. """
    return """
    INSERT INTO outage (outage_id, start_time, etr, category_id, status)
    VALUES %s
    ON CONFLICT (outage_id) DO UPDATE
    SET start_time = EXCLUDED.start_time,
        etr = EXCLUDED.etr,
        category_id = EXCLUDED.category_id,
        status = EXCLUDED.status;
    """


def sql_insert_postcode() -> str:
    """ Insert distinct postcodes; ignore duplicates via ON CONFLICT. """
    return """
    INSERT INTO postcode (postcode)
    VALUES %s
    ON CONFLICT (postcode) DO NOTHING;
    """


def sql_create_tmp_pairs() -> str:
    """ Create a TEMP table to stage (outage_id, postcode) pairs for this run. """
    return "CREATE TEMP TABLE tmp_pairs(outage_id varchar(50), postcode text) ON COMMIT DROP;"


def sql_insert_links_from_tmp() -> str:
    """ Insert outage→postcode links by joining staged pairs to real postcode_ids. """
    return """
    INSERT INTO outage_postcode_link (outage_id, postcode_id)
    SELECT t.outage_id, p.postcode_id
    FROM tmp_pairs t
    JOIN postcode p ON p.postcode = t.postcode
    ON CONFLICT DO NOTHING;
    """


def sql_create_tmp_current_ids() -> str:
    """ Create a TEMP table to stage outage_ids present in the current feed. """
    return "CREATE TEMP TABLE tmp_current_ids(outage_id varchar(50)) ON COMMIT DROP;"


def sql_mark_gone_historical() -> str:
    """ Mark outages as historical if they were 'current' but absent from this run's IDs. """
    return """
    UPDATE outage o
    SET status = 'historical'
    WHERE o.status = 'current'
      AND NOT EXISTS (
        SELECT 1 FROM tmp_current_ids t WHERE t.outage_id = o.outage_id
      );
    """


def to_python(obj: Any) -> Any:
    """
    Coerce pandas scalars into Python-native types psycopg2 understands:
      - pandas.Timestamp -> datetime.datetime (tz-aware)
      - pandas.NaT/NaN   -> None
      - everything else  -> unchanged
    """
    if isinstance(obj, pd.Timestamp):
        return obj.to_pydatetime()
    if obj is None or (not isinstance(obj, str) and pd.isna(obj)):
        return None
    return obj


def df_to_tuples(df: pd.DataFrame, columns: Iterable[str] | None = None) -> List[Tuple]:
    """Convert a DataFrame (optionally selecting columns) to list[tuple] with Python-native values."""
    if columns is not None:
        df = df[list(columns)]
    return [tuple(to_python(v) for v in row.values()) for row in df.to_dict("records")]


def prepare_rows_and_pairs(tables: Dict[str, pd.DataFrame]) -> Dict[str, List[Tuple]]:
    """
    Prepare:
      - outages: list of tuples (outage_id, start_time, etr, category_id, status)
      - postcodes: list of tuples (postcode,)
      - pairs: list of tuples (outage_id, postcode)  <-- used for TEMP table
    """
    outage_df = tables["outage"]
    postcode_df = tables["postcode"]
    link_df = tables["outage_postcode_link"]

    outages = df_to_tuples(
        outage_df,   ["outage_id", "start_time", "etr", "category_id", "status"])
    postcodes = df_to_tuples(postcode_df, ["postcode"])

    # Build link pairs by joining link_df to postcode_df to get postcode TEXT
    pairs_df = link_df.merge(
        postcode_df[["postcode_id", "postcode"]],
        on="postcode_id",
        how="left",
        validate="many_to_one",
    )[["outage_id", "postcode"]].dropna()

    # Normalize postcode text to avoid near-dup issues
    pairs_df["postcode"] = (
        pairs_df["postcode"]
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    pairs = [tuple(row) for row in pairs_df.to_records(index=False)]
    return {"outages": outages, "postcodes": postcodes, "pairs": pairs}


def load_to_rds(tables: Dict[str, pd.DataFrame]) -> Dict[str, int]:
    """
    Load outage-related tables into RDS inside a single transaction.

    Steps:
      0) Stage current outage_ids in TEMP table
      1) UPSERT outage
      2) Mark previously-current but not-in-this-run as historical (only if we staged any IDs)
      3) INSERT postcode (ignore duplicates)
      4) Stage (outage_id, postcode) in TEMP and INSERT links via JOIN

    Returns counts of attempted rows for logging.
    """
    prepared = prepare_rows_and_pairs(tables)
    current_ids = [(row[0],)
                   for row in prepared["outages"]]  # outage_id is first item

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 0) Stage current IDs from this run
            cur.execute(sql_create_tmp_current_ids())
            if current_ids:
                execute_values(
                    cur, "INSERT INTO tmp_current_ids (outage_id) VALUES %s;", current_ids)

            # 1) Upsert outages
            o_count = 0
            if prepared["outages"]:
                execute_values(cur, sql_upsert_outage(), prepared["outages"])
                o_count = len(prepared["outages"])

            # 2) Flip 'gone from feed' rows to historical — only if we had any IDs this run
            if current_ids:
                cur.execute(sql_mark_gone_historical())
            else:
                # Optional: raise to avoid accidental mass flip if feed is empty
                # raise RuntimeError("Empty outage feed detected; aborting to avoid mass flip.")
                pass

            # 3) Insert postcodes
            p_count = 0
            if prepared["postcodes"]:
                execute_values(cur, sql_insert_postcode(),
                               prepared["postcodes"])
                p_count = len(prepared["postcodes"])

            # 4) Insert links via TEMP table + JOIN
            l_count = 0
            if prepared["pairs"]:
                cur.execute(sql_create_tmp_pairs())
                execute_values(
                    cur, "INSERT INTO tmp_pairs (outage_id, postcode) VALUES %s;", prepared["pairs"])
                cur.execute(sql_insert_links_from_tmp())
                l_count = len(prepared["pairs"])

        conn.commit()

    return {"outage": o_count, "postcode": p_count, "outage_postcode_link": l_count}


def orchestrate() -> Dict[str, Any]:
    """
    Run a full ETL cycle: extract -> transform -> load.
    """
    raw_df = generate_outage_csv()  # Extract fresh
    tables = transform_outages(raw_df)  # Transform
    counts = load_to_rds(tables)  # Load (uses get_db_connection())
    return {"ok": True, "counts": counts}


def handler(event, context):
    """AWS Lambda handler (set to load_outages.handler)."""
    try:
        if isinstance(event, dict) and event.get("ping"):
            return {"statusCode": 200, "body": json.dumps({"ok": True, "pong": True})}

        result = orchestrate()
        return {"statusCode": 200, "body": json.dumps(result, default=str)}
    except Exception as e:
        print("ERROR in load_outages.handler:", repr(e))
        return {"statusCode": 500, "body": json.dumps({"ok": False, "error": str(e)})}


if __name__ == "__main__":
    out = orchestrate()
    print(json.dumps(out, indent=2))
