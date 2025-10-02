"""Script with the functions to load the carbon intensity data from the ELEXON API into the database."""

from psycopg2 import connect
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


def query_insert_to_power_reading():
    """SQL query for inserting ELEXON API data to power_readings table"""
    return """
            INSERT INTO power_reading
                (date_time, biomass, coal,
                imports, gas, nuclear, other, hydro, solar,
                wind, price, demand, belgium, denmark, france,
                ireland, netherlands, n_ireland, norway)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ;
            """


def load_power_reading_data(con, power_data: list[list]) -> None:
    """Load the transformed carbon intensity data to the database."""

    query = query_insert_to_power_reading()

    with con.cursor() as cur:
        cur.execute(query, power_data)
    con.commit()
