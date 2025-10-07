import psycopg2
import pandas as pd
from load_outages import get_db_connection


def sql_query_new_outages() -> str:
    """Returns a SQL string to query the database and retrieve postcode and emails affected by current power outages."""
    return """SELECT opl.outage_id, start_time, etr, c2.category, postcode
    FROM outage 
    JOIN outage_postcode_link opl 
    USING(outage_id)
    JOIN category c2 
    USING(category_id)
    JOIN postcode p 
    USING(postcode_id)
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

    email_template = f"""
    <html>
    <head>
        <title>Power Outage Alert</title>
    </head>
    <body>
        <h1>⚠️ Power Outage Alert</h1>
        <h2>We are currently experiencing power outages in your area</h2>
        <table style="width:100%">
            <tr>
                <th>{data.columns}</th>
            </tr>
            <tr>
                <td>{data['postcode']}</td>
            </tr>
        </table>
    </body>
    </html>
    """
    print(email_template)
    # return {
    #     "statusCode": 200,
    #     "body": {
    #         "html_report": email_template
    #     }
    # }


if __name__ == "__main__":
    data = pd.DataFrame(get_outages_data())
    email_body()
