"""Streamlit page: Power Outages — GB Hexagon Map."""

import streamlit as st
import pydeck as pdk
from data import fetch_outage_postcodes, read_df
from power_outages_charts import (
    build_points_from_postcodes,
    build_hex_deck,
    build_outage_time_heatmap
)

# Streamlit page config
st.set_page_config(
    page_title="Power Outages",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Header
st.title("Power Outages")
st.subheader("Geographic Distribution of Power Outages")
st.caption("Visualising GB outage locations aggregated by postcode.")

# Time range toggle for MAP
map_time_window = st.radio(
    "Select Time Range for Map",
    options=["Last 24 Hours", "Last Week"],
    index=1,
    horizontal=True,
)

map_days_back = 1 if map_time_window == "Last 24 Hours" else 7

# Fetch and build map
links_df = fetch_outage_postcodes(days_back=map_days_back, status=None)
points_df = build_points_from_postcodes(links_df)

if points_df.empty:
    st.warning("No outage locations found in this time range.")
    st.stop()

deck = build_hex_deck(
    points_df,
    radius=600,
    elevation_scale=50,
    map_style="mapbox://styles/mapbox/dark-v10",
    opacity=0.7,
)
deck.initial_view_state = pdk.ViewState(
    latitude=52.5, longitude=-2.5, zoom=6, pitch=45)
st.pydeck_chart(deck, use_container_width=True)

# Temporal Patterns in Outages
st.subheader("Temporal Patterns in Outages")
st.caption("A heatmap showing when outages most frequently occur across the week.")

# Independent time range for this chart
heatmap_time_window = st.radio(
    "Select Time Range for Heatmap",
    options=["Last 24 Hours", "Last Week"],
    index=1,
    horizontal=True,
)

heatmap_days_back = 1 if heatmap_time_window == "Last 24 Hours" else 7

sql_heatmap = f"""
SELECT outage_id, start_time
FROM outage
WHERE start_time >= now() - interval '{heatmap_days_back} days';
"""
df_heatmap = read_df(sql_heatmap)
st.altair_chart(build_outage_time_heatmap(
    df_heatmap), use_container_width=True)
