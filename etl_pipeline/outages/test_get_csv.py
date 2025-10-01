""" 
Tests to make sure the get_csv.py file is working as intended. Used mocking to simulate the API 
request without having to directly call it.
"""
import io
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest
from get_csv import generate_outage_csv


@patch("get_csv.requests.get")
@patch("get_csv.pd.DataFrame.to_csv")
def test_generate_outage_csv_success(mock_to_csv, mock_get, tmp_path):
    """ Test to check that when given the data it can retrieve it and store it as a csv. """
    # Fake CSV text to return from requests.get
    fake_csv = "Outage ID,Category,Start Time,ETR,Postcodes\n1,Planned,2025-09-30,2025-10-01,AB12\n"

    # Configure mock requests.get
    mock_response = MagicMock()
    mock_response.text = fake_csv
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    # Call function
    generate_outage_csv()

    # Ensure requests.get called with headers
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    assert "User-Agent" in kwargs["headers"]

    # Ensure pandas read_csv parsed correctly
    df = pd.read_csv(io.StringIO(fake_csv))
    assert len(df) == 1
    assert df.loc[0, "Category"] == "Planned"

    # Ensure to_csv called once to save file
    assert mock_to_csv.called
    _, kwargs = mock_to_csv.call_args
    assert kwargs["index"] is False


@patch("get_csv.requests.get")
def test_generate_outage_csv_http_error(mock_get):
    """ Test to see that if there was an error it reflects that. """
    # Simulate requests raising an HTTP error
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="HTTP Error"):
        generate_outage_csv()
