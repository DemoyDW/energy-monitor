"""
Transform script to modify extracted data and prepare for database insertion
"""
from datetime import datetime, timedelta, timezone
import pandas as pd
from extract_power import get_demand_summary, get_energy_pricing, get_generation_by_type, get_national_energy_generation


def calculate_avg_demand_last_settlement(df: pd.DataFrame) -> float:
    """Calculate average demand for the last settlement."""

    df['startTime'] = pd.to_datetime(df['startTime'], utc=True)

    # Readings come in 5-minute intervals; we are triggering readings at 5 and 35 past the hour.
    # We want all 6 readings within the 30-minute window, so 39 minutes is chosen.
    # 5 minutes are deducted due to the 5 and 35 past triggers.
    end = datetime.now(timezone.utc) - timedelta(minutes=5)
    start = end - timedelta(minutes=39)

    settlement = df[df['startTime'].between(start, end)]
    avg = settlement["demand"].mean().round(2)

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


def transform_power_data(start_time: str, end_time: str) -> list:
    """Put all power, pricing and demand values in to a list ready to be inserted to the database."""

    transformed_data = []

    # Accounting for the fact we are triggering at 5 past the hour for pricing
    # but the settlement readings are for the time on the hour/half-hour
    settlement_time = datetime.now() - timedelta(minutes=5)
    transformed_data.append(settlement_time)

    # National energy generation
    national_generation = get_national_energy_generation(start_time, end_time)
    transformed_data.extend(national_generation['perc'].tolist())

    # Energy price
    pricing = get_energy_pricing(start_time, end_time)
    transformed_data.extend(pricing.head(1))

    # Average demand within past settlement
    demand_summary = get_demand_summary()
    average_demand = calculate_avg_demand_last_settlement(demand_summary)
    transformed_data.append(average_demand)

    # Energy generation by country
    imports = get_generation_by_type(start_time, end_time)
    summary = summarise_energy_generation(imports)
    transformed_data.extend(summary['generation'].tolist())

    return transformed_data
