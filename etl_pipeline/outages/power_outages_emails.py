import psycopg2
import pandas as pd
from load_outages import get_db_connection


def sql_query_new_outages() -> str:
    """Returns a SQL string to query the database and retrieve postcode and emails affected by current power outages."""
    return """SELECT opl.outage_id, start_time, etr, c2.category, postcode, c.customer_id, c.customer_name, c.customer_email
    FROM outage 
    JOIN outage_postcode_link opl 
    USING(outage_id)
    JOIN category c2 
    USING(category_id)
    JOIN postcode p 
    USING(postcode_id)
    JOIN customer_postcode_link cpl 
    USING(postcode_id)
    JOIN customer c 
    USING(customer_id)
    WHERE outage.status 
    LIKE 'current';"""


def get_outages_data() -> dict:
    """Returns a dictionary of current outages, postcodes and customers affected by the power disruptions."""
    with get_db_connection() as conn:
        data = pd.read_sql_query(sql_query_new_outages(), conn)
        return data


def email_body():
    """Generate an html email with relevant postcodes for outages alerts."""
    data = get_outages_data()
    email_data = data[['outage_id', 'postcode',
                       'start_time', 'etr', 'category']]
    table = email_data.to_html()
    email_template = f"""
    <html>
    <head>
        <title>Power Outage Alert</title>
    </head>
    <body>
        <h1>⚠️ Power Outage Alert</h1>
        <h2>We are currently experiencing power outages in your area!</h2>
        {table}
    </body>
    </html>
    """

    print(email_template)


if __name__ == "__main__":
    data = pd.DataFrame(get_outages_data())
    email_body()
