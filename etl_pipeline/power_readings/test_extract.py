"""A test script for power generation data extract script."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from extract import get_utc_settlement_time, get_national_energy_generation, get_demand_summary

# fake_now = datetime(2025, 9, 11, 14, 30, 0)


# @pytest.fixture()
# def fake_datetime_now(monkeypatch):
#     datetime_mock = MagicMock(wraps=datetime)
#     datetime_mock.now.return_value = fake_now
#     monkeypatch.setattr(datetime, "datetime", datetime_mock)


def test_utc_settlement_time(fake_datetime_now):
    fake_now = datetime(2025, 9, 11, 14, 30, 0)
    with patch("datetime") as mock_datetime:
        mock_datetime.now.return_value = fake_now
        mock
        assert get_utc_settlement_time() == []
