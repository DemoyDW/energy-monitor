"""
Tests for extract_outages_csv.generate_outage_csv

- Mocks requests.get so no real network call is made.
- Verifies we parse current CSV schema and (optionally) write to disk.
"""

from pathlib import Path
from unittest.mock import patch, MagicMock
import io
import pandas as pd
import pytest

from extract_outages_csv import generate_outage_csv


def _fake_csv_text() -> str:
    # Matches the live schema you've been using
    return (
        "Upload Date,Region,Incident ID,Confirmed Off,Predicted Off,Restored,Status,Planned,Category,Resource Status,Start Time,ETR,Voltage,Location Latitude,Location Longitude,Postcodes\n"
        "2025-10-01T14:09:00,South West,INCD-1,0,0,0,In Progress,False,LV GENERIC,ONS,2025-10-01T08:29:00,2025-10-01T16:30:00,LV,50.38,-4.02,AB12 1AB\n"
    )


@patch("extract_outages_csv.requests.get")
def test_generate_outage_csv_returns_df_and_writes_when_save_path_given(mock_get, tmp_path):
    """When save_path is passed, we return a DataFrame AND write the CSV to that path."""
    # Mock the HTTP response
    mock_resp = MagicMock()
    mock_resp.text = _fake_csv_text()
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    save_file = tmp_path / "power_outage_ext.csv"

    # Act
    df = generate_outage_csv(save_path=str(save_file))

    # HTTP called with headers containing User-Agent
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert "headers" in kwargs and "User-Agent" in kwargs["headers"]

    # DF content matches our fake row
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.loc[0, "Incident ID"] == "INCD-1"
    assert df.loc[0, "Category"] == "LV GENERIC"
    assert pd.to_datetime(df.loc[0, "Start Time"]
                          ) == pd.Timestamp("2025-10-01T08:29:00")

    # File was written and is readable
    assert save_file.exists()
    disk_df = pd.read_csv(save_file)
    assert len(disk_df) == 1
    assert disk_df.loc[0, "Postcodes"] == "AB12 1AB"


@patch("extract_outages_csv.requests.get")
def test_generate_outage_csv_returns_df_without_writing_when_no_save_path(mock_get, tmp_path):
    """When save_path is NOT passed, we return a DataFrame and do NOT create files."""
    mock_resp = MagicMock()
    mock_resp.text = _fake_csv_text()
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    # Act
    df = generate_outage_csv()

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1

    # Ensure the tmp dir stayed empty (no implicit writes)
    assert list(Path(tmp_path).glob("*")) == []


@patch("extract_outages_csv.requests.get")
def test_generate_outage_csv_http_error(mock_get):
    """HTTP errors bubble up."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = Exception("HTTP Error")
    mock_get.return_value = mock_resp

    with pytest.raises(Exception, match="HTTP Error"):
        generate_outage_csv()
