"""Script with the functions to extract the carbon intensity data from the NESO API."""

from datetime import datetime, timedelta, timezone
from requests import get


def get_utc_settlement_time() -> list[str]:
    """Get the settlement time in UTC."""

    end_time = datetime.now(timezone.utc)
    start_time = (end_time - timedelta(minutes=29))

    return [start_time.isoformat(), end_time.isoformat()]


def extract_carbon_intensity_data(start_time: str, end_time: str) -> list[dict]:
    """Extracts the regional carbon intensity data from the API for a given time window."""

    url = f"https://api.carbonintensity.org.uk/regional/intensity/{start_time}/{end_time}"
    response = get(url)
    data = response.json()["data"][0]["regions"]

    return data
