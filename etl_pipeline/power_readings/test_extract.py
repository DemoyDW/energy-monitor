"""A test script for power generation data extract script."""

from unittest.mock import patch
from datetime import datetime, timedelta, timezone
from extract_power import get_utc_settlement_time, convert_utc_time_string


def test_utc_settlement_time():
    """Testing get_utc_settlement_time. """
    fake_now = datetime(2025, 9, 11, 14, 30, 0, tzinfo=timezone.utc)
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_now
        mock_datetime.return_value = fake_now - timedelta(minutes=34)
        result = get_utc_settlement_time()
        assert isinstance(result, list)
        assert len(result) == 2


def test_utc_settlement_time_29_min():
    """Testing get_utc_settlement_time is in a 29 min time window."""

    result = get_utc_settlement_time()
    start = datetime.fromisoformat(result[0])
    end = datetime.fromisoformat(result[1])
    diff = (end - start).total_seconds() / 60
    assert diff == 34


def test_utc_settlement_time_iso_format():
    """Testing get_utc_settlement_time for time format."""
    fake_now = datetime(2025, 9, 11, 14, 30, 0, tzinfo=timezone.utc)
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_now
        result = get_utc_settlement_time()
        try:
            datetime.fromisoformat(result[0])
            datetime.fromisoformat(result[1])
            success = True
        except ValueError:
            success = False
        assert success


def test_convert_utc_time_string():
    """
    Testing the basic funcionality of the utc time
    string conversion for the Elexon API.
    """

    test_time = ["14:45:15+00:00", "15:15:15+00:00"]

    assert convert_utc_time_string(test_time) == ["14:45:15Z", "15:15:15Z"]
