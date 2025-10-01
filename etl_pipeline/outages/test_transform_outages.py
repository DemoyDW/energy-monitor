# pylint: skip-file
"""
Tests to mkae sure the functionality works correctly, so uses a sample dataset to make 
sure everything runs without using the actual dataset and checks that all the tables
are created properly and they have the correct relations.
"""
import pandas as pd
from transform_outages import transform_outages, CATEGORY_MAP


def make_sample_raw():
    """Make a tiny sample dataframe that looks like the real extract."""
    return pd.DataFrame([
        {
            "Incident ID": "INCD-1",
            "Start Time": "2025-10-01T08:00:00",
            "ETR": "2025-10-01T12:00:00",
            "Category": "LV GENERIC",
            "Postcodes": "AB1 2CD, AB1 2EF"
        },
        {
            "Incident ID": "INCD-2",
            "Start Time": "2025-09-30T10:00:00",
            "ETR": "",
            "Category": "HV DAMAGE",
            "Postcodes": "XY9 8ZZ"
        }
    ])


def test_transform_outages_creates_all_tables():
    raw = make_sample_raw()
    tables = transform_outages(raw)

    # All three tables exist
    assert set(tables.keys()) == {"outage", "postcode", "outage_postcode_link"}


def test_outage_table_columns_and_status():
    raw = make_sample_raw()
    outage_df = transform_outages(raw)["outage"]

    # Required columns
    assert {"outage_id", "start_time", "etr",
            "category_id", "status"} <= set(outage_df.columns)

    # Category IDs mapped correctly
    assert outage_df.loc[outage_df["outage_id"] == "INCD-1",
                         "category_id"].iloc[0] == CATEGORY_MAP["LV GENERIC"]
    assert outage_df.loc[outage_df["outage_id"] == "INCD-2",
                         "category_id"].iloc[0] == CATEGORY_MAP["HV DAMAGE"]

    # Outage with missing ETR should be historical
    assert "historical" in outage_df["status"].values


def test_postcode_and_links():
    raw = make_sample_raw()
    postcode_df = transform_outages(raw)["postcode"]
    link_df = transform_outages(raw)["outage_postcode_link"]

    # Postcodes exploded into 3 unique rows
    assert len(postcode_df) == 3

    # Link table has 3 rows (2 for outage 1, 1 for outage 2)
    assert len(link_df) == 3

    # Each link points to a valid postcode_id
    assert link_df["postcode_id"].isin(postcode_df["postcode_id"]).all()
