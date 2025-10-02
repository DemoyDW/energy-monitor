"""Script with the functions to load the carbon intensity data from the ELEXON API into the database."""

from os import environ as ENV


def query_insert_to_power_reading() -> str:
    """SQL query for inserting power, import, price and demand data into power_readings table"""
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
