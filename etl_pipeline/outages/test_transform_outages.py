"""
Tests to validate the outage transform without hitting the live dataset.
Verifies:
- all three tables are produced
- outage columns and status logic
- postcode explosion and link integrity
"""

import pandas as pd
from transform_outages import transform_outages


def make_sample_raw():
    """Small sample that mimics the extract schema."""
    return pd.DataFrame([
        {
            "Incident ID": "INCD-1",
            "Start Time": "2025-10-01T08:00:00",
            "ETR": "2025-10-01T12:00:00",
            "Category": "LV GENERIC",          # expected -> 2
            "Postcodes": "AB1 2CD, AB1 2EF"
        },
        {
            "Incident ID": "INCD-2",
            "Start Time": "2025-09-30T10:00:00",
            "ETR": "",                          # missing -> historical
            "Category": "HV DAMAGE",            # expected -> 9
            "Postcodes": "XY9 8ZZ"
        }
    ])


def test_transform_outages_creates_all_tables():
    raw = make_sample_raw()
    tables = transform_outages(raw)

    assert set(tables.keys()) == {"outage", "postcode", "outage_postcode_link"}


def test_outage_table_columns_and_status():
    raw = make_sample_raw()
    tables = transform_outages(raw)
    outage_df = tables["outage"]

    # Required columns exist
    assert {"outage_id", "start_time", "etr",
            "category_id", "status"} <= set(outage_df.columns)

    # Category IDs (based on the mapping used in the transform)
    # If the mapping ever changes in code, update these two expected values.
    assert outage_df.loc[outage_df["outage_id"] ==
                         "INCD-1", "category_id"].iloc[0] == 2  # LV GENERIC
    assert outage_df.loc[outage_df["outage_id"] ==
                         "INCD-2", "category_id"].iloc[0] == 9  # HV DAMAGE

    # Missing ETR should mark as historical
    assert outage_df.loc[outage_df["outage_id"] ==
                         "INCD-2", "status"].iloc[0] == "historical"


def test_postcode_and_links():
    raw = make_sample_raw()
    tables = transform_outages(raw)
    postcode_df = tables["postcode"]
    link_df = tables["outage_postcode_link"]

    # Three unique postcodes from the sample
    assert len(postcode_df) == 3

    # Link table: 2 links for INCD-1 + 1 link for INCD-2 = 3
    assert len(link_df) == 3

    # Each link's postcode_id must exist in postcode table
    assert link_df["postcode_id"].isin(postcode_df["postcode_id"]).all()
