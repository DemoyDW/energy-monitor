"""An extract script for the power reading data."""

import requests as req
import pandas as pd
from datetime import datetime, timedelta, timezone


def get_utc_settlement_time() -> list[str]:
    """Get the previous settlement time in UTC."""

    end_time = datetime.now(timezone.utc)
    start_time = (end_time - timedelta(minutes=29))

    return [start_time.isoformat(), end_time.isoformat()]


def get_national_energy_generation(start_time: str, end_time: str) -> dict:
    """Get the national energy generation values for each fuel type."""

    url = f"https://api.carbonintensity.org.uk/generation/{start_time}/{end_time}"
    response = req.get(url)
    data = response.json()["data"][0]["generationmix"]

    return data


def get_demand_summary() -> pd.DataFrame:
    """Get demand summary from API."""

    response = req.get(
        "https://data.elexon.co.uk/bmrs/api/v1/demand/outturn/summary?resolution=minute&format=json")

    demand_data = response.json()

    return pd.DataFrame(demand_data)


def get_energy_pricing(start_time: str, end_time: str) -> dict:
    """Get the market price of energy."""

    start = start_time.replace('+00:00', 'Z')
    end = end_time.replace('+00:00', 'Z')

    url = f"https://data.elexon.co.uk/bmrs/api/v1/balancing/pricing/market-index?from={start}&to={end}"
    response = req.get(url)
    data = response.json()['data']

    return data


BASE_ELEXON = "https://data.elexon.co.uk/bmrs/api/v1"

# Map interconnector codes to country names
INTERCONNECTOR_MAP = {
    "INTELEC": "Belgium (ElecLink)",
    "INTEW": "Ireland (East-West)",
    "INTFR": "France (IFA)",
    "INTIFA2": "France (IFA2)",
    "INTIRL": "Northern Ireland (Moyle)",
    "INTNED": "Netherlands (BritNed)",
    "INTNEM": "Belgium (Nemo Link)",
    "INTNSL": "Norway (North Sea Link)",
    "INTVKL": "Denmark (Viking Link)",
    "INTGRNL": "Ireland (Greenlink)"
}


def get_generation_by_type_summary(start_time, end_time) -> pd.DataFrame:
    """
    Fetch generation outturn summary (by fuel type, half-hourly).
    Flattens nested 'data' column and adds interconnector country mapping.
    """
    url = f"https://data.elexon.co.uk/bmrs/api/v1/generation/outturn/summary?startTime={start_time}&endTime={end_time}&includeNegativeGeneration=true&format=json"
    response = req.get(url)
    response.raise_for_status()
    data = response.json()

    # Extract main data
    if isinstance(data, dict) and "data" in data:
        records = data["data"]
    else:
        records = data

    df = pd.DataFrame(records)

    # Expand nested fuelType/generation list
    df = df.explode("data", ignore_index=True)
    df = pd.concat([df.drop(columns=["data"]),
                   df["data"].apply(pd.Series)], axis=1)

    # Add country column for interconnectors
    df["country"] = df["fuelType"].map(INTERCONNECTOR_MAP)

    df = df.dropna()
    df = df.groupby('country')['generation'].mean()

    return df


def calculate_avg_for_last_settlement(df: pd.DataFrame, column: str) -> float:
    """Calculate average of a numeric column of a dataframe for the last settlement."""

    df['startTime'] = pd.to_datetime(df['startTime'], utc=True)

    end = datetime.now(timezone.utc)
    start = end - timedelta(minutes=34)

    settlement = df[df['startTime'].between(start, end)]
    avg = settlement[column].mean()
    return avg


# def elexon_date_format(start_time, end_time=None):
#     """Creates the iso format for the Elexon api"""

#     date_object = datetime.fromisoformat(start_time)
#     formatted_date = date_object.strftime('%Y-%m-%dT%%3A%MZ')
#     return formatted_date


if __name__ == "__main__":
    now = get_utc_settlement_time()

    # print(get_national_energy_generation(now[0], now[1]))
    # print(get_demand_summary())
    print(now[0])
    # print(elexon_date_format(now[0]))
    print(get_energy_pricing(now[0], now[1]))

    # df = get_generation_by_type_summary()
    # print(df)

    # df2 = get_demand_summary()
    # print(calculate_avg_for_last_settlement(df, "generation"))
    generation_type = (get_generation_by_type_summary(
        now[0].replace('+00:00', 'Z'), now[1].replace('+00:00', 'Z')))
