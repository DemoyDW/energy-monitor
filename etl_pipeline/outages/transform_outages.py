"""
Transform script for National Grid outage data.
Takes the raw outage CSV extract and reshapes it into tables
that match the ERD: outage, postcode, outage_postcode_link.
"""

import pandas as pd

# Map seeded outage categories to IDs
CATEGORY_MAP = {
    "HV ISOLATION": 1,
    "LV GENERIC": 2,
    "LV OVERHEAD": 3,
    "LV UNDERGROUND": 4,
    "HV OVERHEAD": 5,
    "LV ISOLATION": 6,
    "LV FUSE": 7,
    "HV GENERIC": 8,
    "HV DAMAGE": 9,
    "LV DAMAGE": 10,
    "HV FUSE": 11,
    "HV UNDERGROUND": 12,
    "EHV OVERHEAD": 13,
    "HV PLANT": 14
}


def build_outage_table(raw: pd.DataFrame) -> pd.DataFrame:
    """Transform raw outage records, map categories, and tag as current/historical."""
    outage_df = raw[["Incident ID", "Start Time", "ETR", "Category"]].copy()
    outage_df.columns = ["outage_id", "start_time", "etr", "category"]

    # Parse datetimes
    outage_df["start_time"] = pd.to_datetime(
        outage_df["start_time"], utc=True, errors="coerce")
    outage_df["etr"] = pd.to_datetime(
        outage_df["etr"], utc=True, errors="coerce")

    # Map category to seeded IDs
    outage_df["category_id"] = outage_df["category"].map(CATEGORY_MAP)

    # Tag outages as current or historical
    now = pd.Timestamp.utcnow()
    outage_df["status"] = outage_df["etr"].apply(
        lambda x: "current" if pd.notna(x) and x >= now else "historical"
    )

    # Drop raw category text
    outage_df.drop(columns=["category"], inplace=True)

    return outage_df


def build_postcode_table(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create postcode dimension and return exploded outage-postcode pairs."""
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
    """Create the many-to-many link between outages and postcodes."""
    link_df = postcodes.merge(
        postcode_df, left_on="Postcodes", right_on="postcode"
    )[["Incident ID", "postcode_id"]].rename(columns={"Incident ID": "outage_id"})
    return link_df


def transform_outages(raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Master function orchestrating the smaller transforms."""
    outage_df = build_outage_table(raw)
    postcode_df, postcodes = build_postcode_table(raw)
    link_df = build_outage_postcode_link(postcodes, postcode_df)

    return {
        "outage": outage_df,
        "postcode": postcode_df,
        "outage_postcode_link": link_df
    }

