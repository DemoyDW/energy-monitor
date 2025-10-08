"""
Generate HTML report with weekly energy summary to send to subscribers
"""
import pandas as pd
from psycopg2.extras import RealDictCursor
from newsletter_queries import get_db_connection, get_weekly_average, get_average_generation, get_weekly_price, get_avg_carbon_intensity_by_region, get_grouped_generation_mix, get_interconnector_net_flow, get_most_least_carbon_intense_regions, get_national_avg_carbon_intensity, get_total_import_export


def get_subscribers_email(conn) -> list:
    """Retrieve all the emails to send a summary"""

    query = """
        SELECT customer_email 
        FROM customer
        WHERE summary_subscription = TRUE
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    return [row['customer_email'] for row in rows]


def get_all_data(conn) -> dict:
    """Gather all data to create html report"""
    summary_data = {}
    summary_data["total_demand"] = get_weekly_average(conn)[0]
    summary_data["avg_demand"] = get_weekly_average(conn)[1]
    summary_data["avg_price"] = get_weekly_average(conn)[2]
    summary_data["highest_price"] = get_weekly_price(conn, "highest")
    summary_data["lowest_price"] = get_weekly_price(conn, "lowest")
    summary_data["avg_generation"] = get_average_generation(conn)
    summary_data["grouped_generation"] = get_grouped_generation_mix(conn)
    summary_data["inter_flow"] = get_interconnector_net_flow(conn)
    summary_data["total_flow"] = get_total_import_export(
        summary_data["inter_flow"])
    summary_data["national_carbon_avg"] = get_national_avg_carbon_intensity(
        conn)
    summary_data["avg_carbon"] = get_avg_carbon_intensity_by_region(conn)
    summary_data["best_worst"] = get_most_least_carbon_intense_regions(
        summary_data["avg_carbon"])

    return summary_data


def transform_df_to_html(df: pd.DataFrame) -> str:
    """Transform dataframe in to html string"""
    return df.to_html(index=False)


def generate_report_html(energy_data: dict) -> str:
    """Generate html report for email"""

    html = f"""
    <html>
    <head>
        <title>Weekly Energy Report</title>
    </head>
    <body>

    <h1>Weekly Energy Report</h1>

    <h2>Summary Statistics</h2>
    <ul>
        <li><strong>Total Demand:</strong> {energy_data["total_demand"]}</li>
        <li><strong>Average Demand:</strong> {energy_data["avg_demand"]}</li>
        <li><strong>Average Energy Price:</strong> {energy_data["avg_price"]}</li>
        <li><strong>Highest Energy Price:</strong> {energy_data["highest_price"]}</li>
        <li><strong>Lowest Energy Price:</strong> {energy_data["lowest_price"]}</li>
        <li><strong>National Avg. Carbon Intensity:</strong> {energy_data["national_carbon_avg"]}</li>
    </ul>

    <h2>Generation (Average % over 7 Days)</h2>
    {transform_df_to_html(energy_data["avg_generation"])}

    <h2>Grouped Generation (Average % over 7 Days)</h2>
    {transform_df_to_html(energy_data["grouped_generation"])}

    <h2>Average Carbon Intensity by Region</h2>
    {transform_df_to_html(energy_data["avg_carbon"])}

    <h2>Best & Worst Regions (Carbon Intensity)</h2>
    {transform_df_to_html(energy_data["best_worst"])}

    <h2>Interconnector Net Flows</h2>
    {transform_df_to_html(energy_data["inter_flow"])}

    <h2>Import/Export Summary</h2>
    <li><strong>Total Import:</strong> {energy_data["total_flow"][0]}</li>
    <li><strong>Total Export:</strong> {energy_data["total_flow"][1]}</li>

    </body>
    </html>
    """
    return html.replace("\n", "")


def handler(event=None, context=None) -> tuple:
    """Generate summary email and retrieve list of subscriber emails"""
    conn = get_db_connection()
    data = get_all_data(conn)
    summary_emails = generate_report_html(data)
    recipient_emails = get_subscribers_email(conn)

    return (summary_emails, recipient_emails)
