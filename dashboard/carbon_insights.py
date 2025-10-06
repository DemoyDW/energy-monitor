"""Script to display the carbon insights data on the Streamlit dashboard."""
import streamlit as st
from data import get_db_connection, get_carbon_intensity_data
from carbon_insights_charts import create_carbon_intensity_line_graph, create_generation_mix_bar_chart
from datetime import datetime, timedelta


if __name__ == "__main__":

    conn = get_db_connection()
    df = get_carbon_intensity_data(conn)

    st.header("Carbon insights page")

    # Allow a date range selection for the graphs
    date = st.date_input(
        label="Date Range",
        value=(datetime.now() - timedelta(days=3), datetime.now()),
        min_value=df["date_time"].min(),
        max_value="today",
        format="DD-MM-YYYY"
    )

    if len(date) == 2:
        df = df[(df["date_time"].dt.date >= date[0]) & (
            df["date_time"].dt.date <= date[1])]
    else:
        df = df[(df["date_time"].dt.date >= date[0])]

    # Allow the user to select from all the available regions to filter the graphs

    region_list = df["region_name"].unique()

    with st.container(border=True, height=108):
        multi_regions = st.multiselect(
            label="Regions", options=region_list, default=["GB", "Scotland", "England", "Wales"])

    regional_df = df[df["region_name"].isin(multi_regions)]

    # Compare regions on their carbon intensity
    if multi_regions:
        st.plotly_chart(create_carbon_intensity_line_graph(regional_df))
    else:
        st.write("No data selected.")

    # View an individual region's generation mix to identify what is causing their carbon intensity reading
    with st.container(border=True, height=108):
        single_region = st.selectbox(
            label="Region", options=region_list)

    st.plotly_chart(create_generation_mix_bar_chart(df, single_region))
