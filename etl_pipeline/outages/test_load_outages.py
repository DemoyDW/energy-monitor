import pandas as pd
from datetime import datetime
from load_outages import (
    to_python,
    df_to_tuples,
    prepare_rows_and_pairs
)


def test_to_python_converts_timestamp():
    ts = pd.Timestamp("2024-05-01T12:00:00Z")
    result = to_python(ts)
    assert isinstance(result, datetime)


def test_to_python_converts_nat_to_none():
    assert to_python(pd.NaT) is None


def test_to_python_passes_through_other_types():
    assert to_python("ABC") == "ABC"
    assert to_python(123) == 123


def test_df_to_tuples_converts_dataframe_correctly():
    df = pd.DataFrame({
        "a": [1, 2],
        "b": [pd.Timestamp("2024-01-01"), pd.NaT]
    })
    result = df_to_tuples(df)
    assert isinstance(result, list)
    assert all(isinstance(row, tuple) for row in result)
    assert result[0][0] == 1
    assert result[1][1] is None


def test_prepare_rows_and_pairs_merges_correctly():
    outage_df = pd.DataFrame([
        {"outage_id": "O1", "start_time": pd.Timestamp(
            "2024-01-01"), "etr": pd.Timestamp("2024-01-02"), "category_id": 1, "status": "current"}
    ])
    postcode_df = pd.DataFrame([
        {"postcode_id": 1, "postcode": "AB1 2CD"}
    ])
    link_df = pd.DataFrame([
        {"outage_id": "O1", "postcode_id": 1}
    ])
    tables = {"outage": outage_df, "postcode": postcode_df,
              "outage_postcode_link": link_df}

    result = prepare_rows_and_pairs(tables)

    assert "outages" in result
    assert "postcodes" in result
    assert "pairs" in result
    assert result["pairs"][0] == ("O1", "AB1 2CD")
