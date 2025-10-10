"""Queries for summary report of the weeklly newsletter"""
from psycopg2 import connect
from os import environ as ENV
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
import pandas as pd


def get_db_connection():
    """Connect to the postgres database managed by RDS."""
    load_dotenv()

    return connect(database=ENV["DB_NAME"],
                   user=ENV["DB_USERNAME"],
                   password=ENV["DB_PASSWORD"],
                   host=ENV["DB_HOST"],
                   port=ENV["DB_PORT"])


def get_weekly_average(conn) -> list[float]:
    """Returns the total demand, average demand, and average price for the week"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT SUM(demand)AS total_demand, AVG(demand)AS average_demand, 
                          AVG(price)AS average_price
            FROM power_reading
            WHERE date_time >= NOW() - INTERVAL '7 days';
                    """)
        total = cur.fetchone()

    return [round(t, 2) for t in total]


def get_weekly_price(conn, type="highest") -> float:
    """Get highest or lowest price of the week."""
    order = "DESC" if type == "highest" else "ASC"
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT price
            FROM power_reading
            WHERE date_time >= NOW() - INTERVAL '7 days'
            ORDER BY price {order}
            LIMIT 1;
        """)
        price = cur.fetchone()
    return price[0]


def get_average_generation(conn) -> pd.DataFrame:
    """
    Returns the average percentage share of each power source
    over the last 7 days from the power_reading table.
    """
    query = """
            SELECT
                ROUND(AVG(gas)::numeric, 2) AS "Gas",
                ROUND(AVG(coal)::numeric, 2) AS "Coal",
                ROUND(AVG(biomass)::numeric, 2) AS "Biomass",
                ROUND(AVG(nuclear)::numeric, 2) AS "Nuclear",
                ROUND(AVG(hydro)::numeric, 2) AS "Hydro",
                ROUND(AVG(wind)::numeric, 2) AS "Wind",
                ROUND(AVG(solar)::numeric, 2) AS "Solar",
                ROUND(AVG(other)::numeric, 2) AS "Other",
                ROUND(AVG(imports)::numeric, 2) AS "Imports"
            FROM power_reading
            WHERE date_time >= NOW() - INTERVAL '7 days';
        """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        row = cur.fetchone()

    df = pd.DataFrame(list(row.items()), columns=[
                      'Source', 'Average Share (%)'])
    return df


def get_grouped_generation_mix(conn) -> pd.DataFrame:
    """
    Returns average generation mix over the last 7 days grouped into:
    - Renewables (wind, solar, hydro, biomass)
    - Fossil Fuels (gas, coal)
    - Other (nuclear, other, imports)
    """
    query = """
        SELECT
            ROUND(AVG(wind + solar + hydro + biomass)::numeric, 2) AS "Renewable",
            ROUND(AVG(gas + coal)::numeric, 2) AS "Fossil fuels",
            ROUND(AVG(nuclear + other + imports)::numeric, 2) AS "Other"
        FROM power_reading
        WHERE date_time >= NOW() - INTERVAL '7 days';
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        row = cur.fetchone()

    df = pd.DataFrame(list(row.items()), columns=[
                      'Category', 'Average Share (%)'])
    return df


def get_interconnector_net_flow(conn) -> pd.DataFrame:
    """
    Returns the net interconnector flow over the last 7 days.
    Positive = import, Negative = export.
    """
    query = """
        SELECT
            ROUND(SUM(belgium)::numeric, 2) AS "Belgium",
            ROUND(SUM(denmark)::numeric, 2) AS "Denmark",
            ROUND(SUM(france)::numeric, 2) AS "France",
            ROUND(SUM(ireland)::numeric, 2) AS "Ireland",
            ROUND(SUM(netherlands)::numeric, 2) AS "Netherlands",
            ROUND(SUM(n_ireland)::numeric, 2) AS "N. Ireland",
            ROUND(SUM(norway)::numeric, 2) AS "Norway"
        FROM power_reading
        WHERE date_time >= NOW() - INTERVAL '7 days';
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        row = cur.fetchone()

    df = pd.DataFrame(list(row.items()), columns=['Country', 'Net Flow (MW)'])

    directions = []
    for flow in df['Net Flow (MW)']:
        if flow > 0:
            directions.append('Import')
        elif flow < 0:
            directions.append('Export')
        else:
            directions.append('Neutral')

    df['Direction'] = directions

    return df


def get_total_import_export(df: pd.DataFrame) -> tuple:
    """Returns the total energy import and export values over the week."""
    total_import = df.loc[df['Direction'] == 'Import', 'Net Flow (MW)'].sum()
    total_export = df.loc[df['Direction'] ==
                          'Export', 'Net Flow (MW)'].abs().sum()

    return float(total_import), float(total_export)


def get_national_avg_carbon_intensity(conn) -> float:
    """Returns the national average carbon intensity over the last 7 days."""
    query = """
        SELECT ROUND(AVG(carbon_intensity)::numeric, 2) AS national_avg
        FROM carbon_reading
        WHERE date_time >= NOW() - INTERVAL '7 days';
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        result = cur.fetchone()

    return float(result['national_avg'])


def get_avg_carbon_intensity_by_region(conn) -> pd.DataFrame:
    """Returns the average carbon intensity for each region over the week"""
    query = """
        SELECT
            r.region_name,
            ROUND(AVG(cr.carbon_intensity)::numeric, 2) AS avg_carbon_intensity
        FROM carbon_reading cr
        JOIN region r ON cr.region_id = r.region_id
        WHERE cr.date_time >= NOW() - INTERVAL '7 days'
        GROUP BY r.region_name
        ORDER BY avg_carbon_intensity DESC;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    df = pd.DataFrame(rows)
    return df


def get_most_least_carbon_intense_regions(df: pd.DataFrame) -> tuple:
    """Returns the regions with the highest and lowest average carbon intensity over the week."""
    worst_row = df.iloc[0]
    best_row = df.iloc[-1]
    result = pd.DataFrame([
        {'Region': best_row['region_name'],
            'Carbon Intensity': best_row['avg_carbon_intensity'], 'Rank': 'Best Region'},
        {'Region': worst_row['region_name'],
            'Carbon Intensity': worst_row['avg_carbon_intensity'], 'Rank': 'Worst Region'}
    ])
    return result
