"""An extract script for the power reading, pricing and demand data from the Elexon and NESO APIs."""

from datetime import datetime, timedelta, timezone
from requests import get
import pandas as pd


BASE_ELEXON = "https://data.elexon.co.uk/bmrs/api/v1"


def get_utc_settlement_time() -> list[str]:
    """Get the previous settlement time in UTC, suitable for the NESO API endpoints."""

    # We are taking readings for every 30 minute settlement period,
    # 5 minutes after the period has passed (why we subtract 5 minutes from end time).
    # For both APIs, if the time window hits a value in two settlement periods,
    # i.e. window encompasses 11:30-12:00, then both are returned.
    # Hence, 34 minutes has been chosen instead of 35.
    end_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    start_time = (end_time - timedelta(minutes=34))

    return [start_time.isoformat(), end_time.isoformat()]


def convert_utc_time_string(utc_time: list[str]) -> list[str]:
    """
    Converts the UTC settlement time into the necessary 
    format for the Elexon API endpoints.
    """
    return [t.replace('+00:00', 'Z') for t in utc_time]


def get_national_energy_generation(start_time: str, end_time: str) -> dict:
    """Get the national energy generation values for each fuel type."""

    url = f"https://api.carbonintensity.org.uk/generation/{start_time}/{end_time}"

    response = get(url, timeout=20)
    response.raise_for_status()
    generation_data = response.json()["data"][0]["generationmix"]

    return pd.DataFrame(generation_data)


def get_demand_summary() -> pd.DataFrame:
    """Get demand summary from API."""

    url = f"{BASE_ELEXON}/demand/outturn/summary?resolution=minute&format=json"

    response = get(url, timeout=20)
    response.raise_for_status()
    demand_data = response.json()

    return pd.DataFrame(demand_data)


def get_energy_pricing(start_time: str, end_time: str) -> dict:
    """Get the market price of energy."""

    start_time, end_time = convert_utc_time_string([start_time, end_time])

    url = f"{BASE_ELEXON}/balancing/pricing/market-index?from={start_time}&to={end_time}"

    response = get(url, timeout=20)
    response.raise_for_status()
    data = response.json()['data']

    return pd.DataFrame(data)['price']


def get_generation_by_type(start_time: str, end_time: str) -> pd.DataFrame:
    """
    Fetch generation outturn summary (by fuel type, half-hourly).
    Flattens nested 'data' column and adds interconnector country mapping.
    """

    start_time, end_time = convert_utc_time_string([start_time, end_time])

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
