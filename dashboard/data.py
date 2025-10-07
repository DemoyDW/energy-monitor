"""Functions to extract data from the database for the dashboard."""

from psycopg2 import connect
import pandas as pd
from dotenv import load_dotenv
from os import environ as ENV
import streamlit as st


@st.cache_resource
def get_db_connection():
    """Connect to the postgres database managed by RDS."""
    load_dotenv()

    return connect(database=ENV["DB_NAME"],
                   user=ENV["DB_USERNAME"],
                   password=ENV["DB_PASSWORD"],
                   host=ENV["DB_HOST"],
                   port=ENV["DB_PORT"])


@st.cache_data
def get_carbon_intensity_data(_conn) -> pd.DataFrame:

    query = "SELECT * FROM carbon_reading JOIN region USING (region_id);"

    with _conn.cursor() as cur:
        cur.execute(query)
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    return pd.DataFrame(data, columns=column_names)
