"""An extract script for the power reading, pricing and demand data from the Elexon and NESO APIs."""

from datetime import datetime, timedelta, timezone
from requests import get
import pandas as pd


BASE_ELEXON = "https://data.elexon.co.uk/bmrs/api/v1"


def get_utc_settlement_time() -> list[str]:
    """Get the previous settlement time in UTC."""

    # We are taking readings for every 30 minute settlement period,
    # 5 minutes after the period has passed (why we subtract 5 minutes from end time).
    # For both APIs, if the time window hits a value in two settlement periods,
    # i.e. window encompasses 11:30-12:00, then both are returned.
    # Hence, 34 minutes has been chosen instead of 35.
    end_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    start_time = (end_time - timedelta(minutes=34))

    return [start_time.isoformat(), end_time.isoformat()]


def get_national_energy_generation(start_time: str, end_time: str) -> dict:
    """Get the national energy generation values for each fuel type."""

    url = f"https://api.carbonintensity.org.uk/generation/{start_time}/{end_time}"
    response = get(url, timeout=20)
    data = response.json()["data"][0]["generationmix"]

    return pd.DataFrame(data)


def get_demand_summary() -> pd.DataFrame:
    """Get demand summary from API."""

    response = get(
        f"{BASE_ELEXON}/demand/outturn/summary?resolution=minute&format=json", timeout=20)

    demand_data = response.json()

    return pd.DataFrame(demand_data)


def get_energy_pricing(start_time: str, end_time: str) -> dict:
    """Get the market price of energy."""

    start = start_time.replace('+00:00', 'Z')
    end = end_time.replace('+00:00', 'Z')

    url = f"{BASE_ELEXON}/balancing/pricing/market-index?from={start}&to={end}"
    response = get(url, timeout=20)
    data = response.json()['data']

    return pd.DataFrame(data)['price']


def get_generation_by_type(start_time: str, end_time: str) -> pd.DataFrame:
    """
    Fetch generation outturn summary (by fuel type, half-hourly).
    Flattens nested 'data' column and adds interconnector country mapping.
    """

    # Necessary string transformation for this API endpoint to work
    start_time = start_time.replace('+00:00', 'Z'),
    end_time = end_time.replace('+00:00', 'Z')

    url = f"{BASE_ELEXON}/generation/outturn/summary?startTime={start_time}&endTime={end_time}&includeNegativeGeneration=true&format=json"
    response = get(url, timeout=20)
    response.raise_for_status()
    data = response.json()

    # Extract main data
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
    else:
        records = data

    df = pd.DataFrame(records)

    return df
