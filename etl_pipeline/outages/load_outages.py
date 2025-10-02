"""
Load outage data into RDS

- Reads DB creds from .env (DB_HOST, DB_PORT, DB_DB, DB_USER, DB_PASSWORD)
- Upserts `outage`
- Inserts `postcode` (ignore duplicates)
- Inserts `outage_postcode_link` by staging (outage_id, postcode) into a TEMP table
  and resolving postcode_id
"""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from transform_outages import transform_outages
from extract_outages_csv import generate_outage_csv


def load_db_config() -> Dict[str, Any]:
    """Read DB connection settings from environment variables."""
    load_dotenv()
    return {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_DB"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }


def sql_upsert_outage() -> str:
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
    return """
    INSERT INTO postcode (postcode)
    VALUES %s
    ON CONFLICT (postcode) DO NOTHING;
    """


def sql_create_tmp_pairs() -> str:
    return "CREATE TEMP TABLE tmp_pairs(outage_id varchar(50), postcode text) ON COMMIT DROP;"


def sql_insert_links_from_tmp() -> str:
    return """
    INSERT INTO outage_postcode_link (outage_id, postcode_id)
    SELECT t.outage_id, p.postcode_id
    FROM tmp_pairs t
    JOIN postcode p ON p.postcode = t.postcode
    ON CONFLICT DO NOTHING;
    """


def to_python(obj: Any) -> Any:
    """
    Coerce pandas/NumPy scalars into Python-native objects psycopg2 understands.
    - pandas.Timestamp to datetime.datetime (tz-aware)
    - pandas.NaT/NaN to None
    - everything else to unchanged
    """
    if isinstance(obj, pd.Timestamp):
        return obj.to_pydatetime()
    try:
        if obj is None or (not isinstance(obj, str) and pd.isna(obj)):
            return None
    except Exception:
        pass
    return obj


def df_to_tuples(df: pd.DataFrame, columns: Iterable[str] | None = None) -> List[Tuple]:
    """
    Convert a DataFrame (optionally selecting columns) into a list of tuples
    with Python-native values (no NaT/NaN).
    """
    if columns is not None:
        df = df[list(columns)]
    return [tuple(to_python(v) for v in row.values()) for row in df.to_dict("records")]


def prepare_rows_and_pairs(tables: Dict[str, pd.DataFrame]) -> Dict[str, List[Tuple]]:
    """
    Prepare:
      - outages: list of tuples (outage_id, start_time, etr, category_id, status)
      - postcodes: list of tuples (postcode,)
      - pairs: list of tuples (outage_id, postcode) 
    """
    outage_df = tables["outage"]
    postcode_df = tables["postcode"]
    link_df = tables["outage_postcode_link"]

    # Outages & postcodes as usual
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

    # Optional normalization (helps avoid near-dup postcodes with weird spacing/case)
    pairs_df["postcode"] = (
        pairs_df["postcode"]
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    pairs = [tuple(row) for row in pairs_df.to_records(index=False)]
    return {"outages": outages, "postcodes": postcodes, "pairs": pairs}


def load_to_rds(tables: Dict[str, pd.DataFrame], conn_params: Dict[str, Any]) -> Dict[str, int]:
    """
    Load outage-related tables into RDS inside a single transaction.
    Uses a TEMP table to resolve outage_postcode_link via postcode text.
    Returns counts of attempted rows per table for logging.
    """
    prepared = prepare_rows_and_pairs(tables)

    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            # Upsert outages
            o_count = 0
            if prepared["outages"]:
                execute_values(cur, sql_upsert_outage(), prepared["outages"])
                o_count = len(prepared["outages"])

            # Insert postcodes (ignore duplicates)
            p_count = 0
            if prepared["postcodes"]:
                execute_values(cur, sql_insert_postcode(),
                               prepared["postcodes"])
                p_count = len(prepared["postcodes"])

            # Stage link pairs and insert via JOIN
            l_count = 0
            if prepared["pairs"]:
                cur.execute(sql_create_tmp_pairs())
                execute_values(
                    cur, "INSERT INTO tmp_pairs (outage_id, postcode) VALUES %s;", prepared["pairs"])
                cur.execute(sql_insert_links_from_tmp())
                l_count = len(prepared["pairs"])

        conn.commit()

    return {"outage": o_count, "postcode": p_count, "outage_postcode_link": l_count}
