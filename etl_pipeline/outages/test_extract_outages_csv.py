# pylint: skip-file
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import pytest

from extract_outages_csv import generate_outage_csv


@patch("extract_outages_csv.requests.get")
def test_generate_outage_csv_success(mock_get, mocked_response, tmp_path):
    """Returns a DataFrame and writes when save_path is provided."""
    mock_get.return_value = mocked_response
    save_file: Path = tmp_path / "power_outage_ext.csv"

    df = generate_outage_csv(save_path=str(save_file))

    _, kwargs = mock_get.call_args
    assert "headers" in kwargs and "User-Agent" in kwargs["headers"]

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {"Incident ID", "Category", "Postcodes"} <= set(df.columns)

    assert save_file.exists()
    disk_df = pd.read_csv(save_file)
    assert not disk_df.empty


@patch("extract_outages_csv.requests.get")
def test_generate_outage_csv_http_error(mock_get):
    """HTTP errors bubble up."""
    class _Err:
        text = ""

        def raise_for_status(self):
            raise Exception("HTTP Error")
    mock_get.return_value = _Err()

    with pytest.raises(Exception, match="HTTP Error"):
        generate_outage_csv()
