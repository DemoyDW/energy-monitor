"""Tests for the extract carbon intensity functions"""

from extract_carbon import get_utc_settlement_time


def test_get_utc_settlement_time():

    test_utc = get_utc_settlement_time()

    assert isinstance(test_utc, list)
    assert all(isinstance(t, str) for t in test_utc)
