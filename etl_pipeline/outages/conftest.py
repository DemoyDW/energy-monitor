import pytest
from unittest.mock import MagicMock


@pytest.fixture
def fake_csv_text() -> str:
    return (
        "Upload Date,Region,Incident ID,Confirmed Off,Predicted Off,Restored,Status,Planned,Category,Resource Status,Start Time,ETR,Voltage,Location Latitude,Location Longitude,Postcodes\n"
        "2025-10-01T14:09:00,South West,INCD-1,0,0,0,In Progress,False,LV GENERIC,ONS,2025-10-01T08:29:00,2025-10-01T16:30:00,LV,50.38,-4.02,AB12 1AB\n"
    )


@pytest.fixture
def mocked_response(fake_csv_text):
    resp = MagicMock()
    resp.text = fake_csv_text
    resp.raise_for_status = MagicMock()
    return resp
