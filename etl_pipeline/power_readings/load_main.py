"""Script that compiles both ETL processes to upload the power and carbon intensity data to the database."""

from extract_carbon import extract_carbon_intensity_data
from transform_carbon import transform_carbon_intensity_data
from load_carbon import load_carbon_intensity_data, get_db_connection

from extract_power import get_utc_settlement_time
from transform_power import transform_power_data
from load_power import load_power_reading_data


def handler(event=None, context=None) -> dict:
    """Load the data from the carbon and power ETL processes to the database."""

    start_time, end_time = get_utc_settlement_time()

    carbon_data = extract_carbon_intensity_data(start_time, end_time)
    carbon_data = transform_carbon_intensity_data(carbon_data)

    # Transform gets the data inside of the function
    power_data = transform_power_data(start_time, end_time)

    with get_db_connection() as conn:
        load_carbon_intensity_data(conn, carbon_data)
        load_power_reading_data(conn, power_data)

    return {"statusCode": 200}
