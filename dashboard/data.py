"""Functions to extract data from the database for the dashboard."""

from __future__ import annotations
from os import environ as ENV
from psycopg2 import connect
import pandas as pd
from dotenv import load_dotenv
import streamlit as st


@st.cache_resource(show_spinner=False)
def get_db_connection():
    """Connect to the Postgres database on RDS using env vars."""
    load_dotenv()
    return connect(
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        sslmode=ENV.get("DB_SSLMODE", "require")
    )


@st.cache_data(show_spinner=False)
def read_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    with get_db_connection() as conn:
        return pd.read_sql_query(sql, conn, params=params or {})


@st.cache_data(show_spinner=False)
def get_carbon_intensity_data(days_back: int = 7) -> pd.DataFrame:
    """
    Fetch carbon intensity data with region info for the past N days.
    """
    sql = """
        SELECT c.*, r.region_name
        FROM carbon_reading c
        JOIN region r USING (region_id)
        WHERE c.date_time >= now() - make_interval(days => %(days)s)
        ORDER BY c.date_time;
    """
    return read_df(sql, {"days": days_back})


@st.cache_data(show_spinner=False)
def fetch_outage_postcodes(days_back: int = 7, status: str | None = "current") -> pd.DataFrame:
    """
    Return outage_id, status, and postcode for outages in the last N days.
    """
    clauses = ["o.start_time >= now() - make_interval(days => %(days)s)"]
    params = {"days": days_back}

    if status in ("current", "historical"):
        clauses.append("o.status = %(status)s")
        params["status"] = status

    where_sql = " AND ".join(clauses)

    sql = f"""
        SELECT 
            o.outage_id,
            o.status,
            p.postcode
        FROM outage o
        JOIN outage_postcode_link l ON l.outage_id = o.outage_id
        JOIN postcode p ON p.postcode_id = l.postcode_id
        WHERE {where_sql}
        ORDER BY o.start_time DESC;
    """

    return read_df(sql, params)


@st.cache_data(show_spinner=False)
def fetch_power_readings(days_back: int = 7) -> pd.DataFrame:
    """
    Fetch all power generation and interconnector readings for the last N days.
    """
    sql = """
        SELECT date_time, gas, coal, biomass, nuclear, hydro,
               imports, other, wind, solar, price, demand,
               france, belgium, netherlands, denmark, norway, ireland, n_ireland
        FROM power_reading
        WHERE date_time >= now() - make_interval(days => %(days)s)
        ORDER BY date_time;
    """
    return read_df(sql, {"days": days_back})


@st.cache_data(show_spinner=False)
def fetch_energy_prices(days_back: int = 7) -> pd.DataFrame:
    """
    Fetch price and demand data from the power_reading table for the past N days.
    Returns columns: date_time, price, demand.
    """
    sql = """
        SELECT date_time, price, demand
        FROM power_reading
        WHERE date_time >= now() - make_interval(days => %(days)s)
        ORDER BY date_time;
    """
    return read_df(sql, {"days": days_back})
