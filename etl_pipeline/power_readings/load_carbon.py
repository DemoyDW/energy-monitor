"""Script with the functions to load the carbon intensity data from the NESO API into the database."""

from psycopg2 import connect
from psycopg2.extras import execute_values
from os import environ as ENV
from dotenv import load_dotenv


def get_db_connection():
    """Connect to the postgres database managed by RDS."""
    load_dotenv()

    return connect(database=ENV["DB_NAME"],
                   user=ENV["DB_USERNAME"],
                   password=ENV["DB_PASSWORD"],
                   host=ENV["DB_HOST"],
                   port=ENV["DB_PORT"])


def sql_insert_carbon_reading() -> str:
    """SQL query for inserting the data into the carbon_reading table."""

    return """
            INSERT INTO carbon_reading
                (date_time, carbon_intensity, region_id,
                gas, coal, biomass, nuclear, hydro, imports,
                other, wind, solar)
            VALUES
                %s
            ;
            """


def load_carbon_intensity_data(conn, carbon_data: list[list]) -> None:
    """Load the transformed carbon intensity data to the database."""

    query = sql_insert_carbon_reading()

    with conn.cursor as cur:
        execute_values(cur, query, carbon_data)
        conn.commit()
