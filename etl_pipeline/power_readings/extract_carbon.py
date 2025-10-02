"""Script with the functions to extract the carbon intensity data from the NESO API."""

from datetime import datetime, timedelta, timezone
from requests import get


def get_utc_settlement_time(end_time: datetime = datetime.now(timezone.utc)) -> list[str]:
    """Get the settlement time in UTC."""

    # We are taking readings for every 30 minute settlement period, however
    #  for this API, if the time window hits a value in two settlement periods,
    #  both are returned. Hence, 29 minutes has been chosen
    start_time = end_time - timedelta(minutes=29)

    return [start_time.isoformat(), end_time.isoformat()]


def extract_carbon_intensity_data(start_time: str, end_time: str) -> list[dict]:
    """Extracts the regional carbon intensity data from the API for a given time window."""

    url = f"https://api.carbonintensity.org.uk/regional/intensity/{start_time}/{end_time}"
    response = get(url, timeout=10)

    data = response.json()["data"][0]["regions"]

    return data
