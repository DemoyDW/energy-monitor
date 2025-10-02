"""
Transform script to modify extracted data and prepare for database insertion
"""
from datetime import datetime, timedelta, timezone
import pandas as pd
from extract import get_demand_summary, get_energy_pricing, get_generation_by_type, get_national_energy_generation


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


def summarize_energy_generation(df: pd.DataFrame, mappings: dict) -> pd.DataFrame:
    """Summarises import and export of the last settlement"""

    # Expand nested fuelType/generation list
    df = df.explode("data", ignore_index=True)
    df = pd.concat([df.drop(columns=["data"]),
                   df["data"].apply(pd.Series)], axis=1)

    # Add country column for interconnectors
    df["country"] = df["fuelType"].map(mappings)

    df = df.dropna()
    df = df.groupby('country')['generation'].mean().reset_index()

    return df


def combine_company_generation(df: pd.DataFrame) -> pd.DataFrame:
    """Combine different parts of a country to 1 country"""
    # map to group all relevant countries in to one
    country_map = {
        'Belgium (ElecLink)': 'Belgium',
        'Belgium (Nemo Link)': 'Belgium',
        'France (IFA)': 'France',
        'France (IFA2)': 'France',
        'Ireland (East-West)': 'Ireland',
        'Ireland (Greenlink)': 'Ireland',
        'Denmark (Viking Link)': 'Denmark',
        'Netherlands (BritNed)': 'Netherlands',
        'Northern Ireland (Moyle)': 'Northern Ireland',
        'Norway (North Sea Link)': 'Norway',
    }

    df['country'] = df['country'].map(country_map)

    result = df.groupby('country', as_index=False)['generation'].sum()

    result['generation'] = result['generation'].round(2)

    return result


def transform_all_data(time: list) -> list:
    """Put all values in to a list ready to be inserted to database"""
    interconnerctor_map = {
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
    summary = summarize_energy_generation(imports, interconnerctor_map)
    combined_countries = combine_company_generation(summary)
    all_data.extend(combined_countries['generation'].tolist())

    return all_data
