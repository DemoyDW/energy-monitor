"""Streamlit page for Carbon Insights."""

from shapely.geometry import mapping
import json
import altair as alt
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import geopandas as gpd
import pydeck as pdk
from data import get_carbon_intensity_data
from carbon_insights_charts import (
    create_carbon_intensity_line_graph,
    create_generation_mix_bar_chart, prepare_choropleth_data, create_carbon_heatmap
)

# PAGE CONFIG
st.set_page_config(page_title="Carbon Insights", layout="wide")
st.header("Carbon Insights")


# LOAD DATA
st.caption("Live regional carbon intensity and generation mix data")

df = get_carbon_intensity_data()
df["date_time"] = pd.to_datetime(df["date_time"])

# DATE RANGE SELECTION
min_date = df["date_time"].min().date()
max_date = df["date_time"].max().date()

# Default to last 3 days, or fallback to full range if dataset too short
default_start = max(max_date - timedelta(days=3), min_date)

if (max_date - min_date).days < 3:
    st.warning(
        f"Not enough data to show a 3-day range. Displaying available range from {min_date} to {max_date}."
    )

date_range = st.date_input(
    label="Select Date Range",
    value=(default_start, max_date),
    min_value=min_date,
    max_value=max_date,
    format="DD-MM-YYYY"
)

# Apply date filter
if len(date_range) == 2:
    df = df[(df["date_time"].dt.date >= date_range[0]) &
            (df["date_time"].dt.date <= date_range[1])]
else:
    df = df[df["date_time"].dt.date == date_range[0]]

# REGION MULTISELECT
region_list = sorted(df["region_name"].unique())

with st.container():
    multi_regions = st.multiselect(
        label="Compare multiple regions",
        options=region_list,
        default=region_list[:3],
        help="Select regions to compare carbon intensity over time"
    )

regional_df = df[df["region_name"].isin(multi_regions)]


# Regional Carbon Intensity Over Time
st.subheader("Regional Carbon Intensity Over Time")
st.caption(
    "Displays how carbon intensity varies across regions within the selected period.")

if not regional_df.empty:
    st.plotly_chart(create_carbon_intensity_line_graph(
        regional_df), use_container_width=True)
else:
    st.warning("No data available for the selected regions and date range.")


# Generation Mix for Single Region
st.subheader("Generation Mix by Region")
st.caption(
    "Breakdown of average energy generation sources contributing to each region’s intensity.")

with st.container():
    single_region = st.selectbox(
        label="Select a region to explore its generation mix",
        options=region_list,
        index=0
    )

st.plotly_chart(create_generation_mix_bar_chart(
    df, single_region), use_container_width=True)

st.subheader("Average Carbon Intensity by UK Region")

choropleth_df = prepare_choropleth_data(df)
geojson_path = "data/uk_regions_adjusted.geojson"

st.plotly_chart(create_carbon_heatmap(choropleth_df), use_container_width=True)
