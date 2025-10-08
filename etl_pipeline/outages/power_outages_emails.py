"""Writes a email template for power outages alerts and returns a list of emails of affected customers."""
import psycopg2
import pandas as pd
from load_outages import get_db_connection




    def get_outages_data(conn) -> pd.DataFrame:
        """Returns a dataframe of current outages, postcodes and customers affected by the power disruptions."""
        
        query = """SELECT opl.outage_id, start_time, etr, c2.category, postcode, c.customer_id, c.customer_name, c.customer_email
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

        return pd.read_sql_query(query, conn)


def email_body(outage_data: pd.DataFrame):
    """Generate an html email with relevant postcodes for outages alerts."""
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

    return email_template


def get_customer_emails(outage_data: pd.DataFrame) -> list[str]:
    """Returns a list of customer emails who were affected by the power outages."""
    return outage_data["customer_email"].tolist()


