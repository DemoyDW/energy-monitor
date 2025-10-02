"""
Transform script to modify extracted data and prepare for database insertion
"""
from datetime import datetime, timedelta, timezone
import pandas as pd
from extract_power import get_demand_summary, get_energy_pricing, get_generation_by_type, get_national_energy_generation


def calculate_avg_for_last_settlement(df: pd.DataFrame, column: str) -> float:
    """Calculate average of a numeric column of a dataframe for the last settlement."""

    df['startTime'] = pd.to_datetime(df['startTime'], utc=True)

    # Readings come in 5-minute intervals; we are triggering readings at 5 and 35 past the hour.
    # We want all 6 readings within the 30-minute window, so 39 minutes is chosen.
    # 5 minutes are deducted due to the 5 and 35 past triggers.
    end = datetime.now(timezone.utc) - timedelta(minutes=5)
    start = end - timedelta(minutes=39)

    settlement = df[df['startTime'].between(start, end)]
    avg = settlement[column].mean()

    return avg


def summarise_energy_generation(df: pd.DataFrame) -> pd.DataFrame:
    """Summarises import and export of the previous settlement."""

    country_map = {
        "INTELEC": "Belgium",
        "INTEW": "Ireland",
        "INTFR": "France",
        "INTIFA2": "France",
        "INTIRL": "Northern Ireland",
        "INTNED": "Netherlands",
        "INTNEM": "Belgium",
        "INTNSL": "Norway",
        "INTVKL": "Denmark",
        "INTGRNL": "Ireland"
    }

    # Expand nested fuelType/generation list
    df = df.explode("data", ignore_index=True)
    df = pd.concat([df.drop(columns=["data"]),
                   df["data"].apply(pd.Series)], axis=1)

    # Add country column for interconnectors
    df["country"] = df["fuelType"].map(country_map)

    # This will remove local readings and leave only imports
    # as only imports are included in the mapping
    df = df.dropna()

    df = df.groupby('country')['generation'].mean().round(2).reset_index()

    return df


def transform_all_data(time: list) -> list:
    """Put all values in to a list ready to be inserted to database."""

    # We are taking reading every 30 minutes, but triggering at 35 past
    all_data = []
    current_time = datetime.now() - timedelta(minutes=5)
    all_data.append(current_time.isoformat())

    # National energy generation
    national_generation = get_national_energy_generation(time[0], time[1])
    all_data.extend(national_generation['perc'].tolist())

    # Energy price
    pricing = get_energy_pricing(time[0], time[1])
    all_data.extend(pricing.head(1))

    # Average demand within past settlement
    demand_summary = get_demand_summary()
    average_demand = round(float(calculate_avg_for_last_settlement(
        demand_summary, "demand")), 2)
    all_data.append(average_demand)

    # Energy generation by country
    imports = get_generation_by_type(time[0].replace(
        '+00:00', 'Z'), time[1].replace('+00:00', 'Z'))
    summary = summarise_energy_generation(imports)
    all_data.extend(summary['generation'].tolist())

    return all_data
