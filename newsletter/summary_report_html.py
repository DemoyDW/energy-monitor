"""
Generate HTML report with weekly energy summary to send to subscribers
"""
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


def generate_report_html(conn) -> str:
    """Generate html report for email"""

    tot_demand = get_weekly_average(conn)[0]
    avg_demand = get_weekly_average(conn)[1]
    avg_price = get_weekly_average(conn)[2]
    highest_price = get_weekly_price(conn, "highest")
    lowest_price = get_weekly_price(conn, "lowest")
    avg_generation = get_average_generation(conn)
    grouped_generation = get_grouped_generation_mix(conn)
    inter_flow = get_interconnector_net_flow(conn)
    total_flow = get_total_import_export(inter_flow)
    national_carbon_avg = get_national_avg_carbon_intensity(conn)
    avg_carbon = get_avg_carbon_intensity_by_region(conn)
    best_worst = get_most_least_carbon_intense_regions(avg_carbon)

    # Convert to html tables
    avg_generation_html = avg_generation.to_html(index=False)
    grouped_generation_html = grouped_generation.to_html(index=False)
    best_worst_html = best_worst.to_html(index=False)
    inter_flow_html = inter_flow.to_html(index=False)
    avg_carbon_html = avg_carbon.to_html(index=False)

    html = f"""
    <html>
    <head>
        <title>Weekly Energy Report</title>
    </head>
    <body>

    <h1>Weekly Energy Report</h1>

    <h2>Summary Statistics</h2>
    <ul>
        <li><strong>Total Demand:</strong> {tot_demand}</li>
        <li><strong>Average Demand:</strong> {avg_demand}</li>
        <li><strong>Average Energy Price:</strong> {avg_price}</li>
        <li><strong>Highest Energy Price:</strong> {highest_price}</li>
        <li><strong>Lowest Energy Price:</strong> {lowest_price}</li>
        <li><strong>National Avg. Carbon Intensity:</strong> {national_carbon_avg}</li>
    </ul>

    <h2>Generation (Average % over 7 Days)</h2>
    {avg_generation_html}

    <h2>Grouped Generation (Average % over 7 Days)</h2>
    {grouped_generation_html}

    <h2>Average Carbon Intensity by Region</h2>
    {avg_carbon_html}

    <h2>Best & Worst Regions (Carbon Intensity)</h2>
    {best_worst_html}

    <h2>Interconnector Net Flows</h2>
    {inter_flow_html}

    <h2>Import/Export Summary</h2>
    <li><strong>Total Import:</strong> {total_flow[0]}</li>
    <li><strong>Total Export:</strong> {total_flow[1]}</li>

    </body>
    </html>
    """
    return html


def handler(event=None, context=None) -> tuple:
    """Generate summary email and retrieve list of subscriber emails"""
    conn = get_db_connection()
    summary_emails = generate_report_html(conn)
    recipient_emails = get_subscribers_email(conn)

    return (summary_emails, recipient_emails)


if __name__ == "__main__":
    print(handler())
