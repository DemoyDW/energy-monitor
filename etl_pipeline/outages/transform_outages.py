"""
Transform script for National Grid outage data.
Reshapes raw CSV into: outage, postcode, outage_postcode_link.
Parses UK local time, maps category -> id, adds status, and ensures no NaT.
"""

import pandas as pd
from datetime import datetime


def parse_uk_time(series: pd.Series) -> pd.Series:
    """ Parses the datetimes in pandas as UK local time. """
    return (
        pd.to_datetime(series, errors="coerce")
        .dt.tz_localize("Europe/London", ambiguous="NaT", nonexistent="NaT")
    )


def _to_py_dt_or_none(x):
    """ Converts value to a datetime with tzinfo or None. """
    if isinstance(x, pd.Timestamp):
        return x.to_pydatetime()
    if x is None or pd.isna(x):
        return None
    return x


def build_outage_table(raw: pd.DataFrame) -> pd.DataFrame:
    """ Transform the raw CSV into the `outage` fact table. """

    CATEGORY_MAP = {
        "HV ISOLATION": 1, "LV GENERIC": 2, "LV OVERHEAD": 3, "LV UNDERGROUND": 4,
        "HV OVERHEAD": 5, "LV ISOLATION": 6, "LV FUSE": 7, "HV GENERIC": 8,
        "HV DAMAGE": 9, "LV DAMAGE": 10, "HV FUSE": 11, "HV UNDERGROUND": 12,
        "EHV OVERHEAD": 13, "HV PLANT": 14,
    }

    outage_df = raw[["Incident ID", "Start Time", "ETR", "Category"]].copy()
    outage_df.columns = ["outage_id", "start_time", "etr", "category"]

    outage_df["start_time"] = parse_uk_time(outage_df["start_time"])
    outage_df["etr"] = parse_uk_time(outage_df["etr"])

    outage_df["category_id"] = outage_df["category"].map(CATEGORY_MAP)

    now_uk = pd.Timestamp.now(tz="Europe/London")
    outage_df["status"] = outage_df["etr"].apply(
        lambda x: "current" if pd.notna(x) and x >= now_uk else "historical"
    )

    outage_df.drop(columns=["category"], inplace=True)

    # force object dtype to avoid pandas coercion
    for col in ["start_time", "etr"]:
        outage_df[col] = outage_df[col].astype("object")
        outage_df[col] = [_to_py_dt_or_none(x) for x in outage_df[col]]

    # sanity assertions (will raise if any NaT/Timestamp remains)
    assert all(isinstance(x, (type(None), datetime))
               for x in outage_df["start_time"])
    assert all(isinstance(x, (type(None), datetime)) for x in outage_df["etr"])

    return outage_df


def build_postcode_table(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ Create the postcode dimension and an exploded intermediary. """

    postcodes = (
        raw[["Incident ID", "Postcodes"]]
        .dropna()
        .assign(Postcodes=lambda x: x["Postcodes"].str.split(","))
        .explode("Postcodes")
    )
    postcodes["Postcodes"] = postcodes["Postcodes"].str.strip()

    postcode_df = pd.DataFrame({"postcode": postcodes["Postcodes"].unique()})
    postcode_df["postcode_id"] = range(1, len(postcode_df) + 1)
    return postcode_df, postcodes


def build_outage_postcode_link(postcodes: pd.DataFrame, postcode_df: pd.DataFrame) -> pd.DataFrame:
    """ Create the `outage_postcode_link` table (using temporary postcode_ids). """

    link_df = postcodes.merge(
        postcode_df, left_on="Postcodes", right_on="postcode"
    )[["Incident ID", "postcode_id"]].rename(columns={"Incident ID": "outage_id"})
    return link_df


def transform_outages(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """ Orchestrate transforms and return all three tables. """

    outage_df = build_outage_table(raw)
    postcode_df, postcodes = build_postcode_table(raw)
    link_df = build_outage_postcode_link(postcodes, postcode_df)
    return {"outage": outage_df, "postcode": postcode_df, "outage_postcode_link": link_df}


if __name__ == "__main__":
    raw = pd.read_csv("power_outage_ext.csv")
    tables = transform_outages(raw)

    for name, df in tables.items():
        print(f"\n--- {name.upper()} ({len(df)} rows) ---")
        print(df.head(10))

    out = tables["outage"]
    print("start_time types:", {type(x) for x in out["start_time"].head(10)})
    print("etr types:", {type(x) for x in out["etr"].head(10)})
