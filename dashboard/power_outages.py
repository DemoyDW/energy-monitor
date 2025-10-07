"""Streamlit page: Power Outages — UK Hexagon Map (Dark Mode)."""

import streamlit as st
import pydeck as pdk
from data import fetch_outage_postcodes, read_df
from power_outages_charts import build_points_from_postcodes, build_hex_deck, build_outage_time_heatmap, build_avg_outage_duration_chart

# Streamlit page config
st.set_page_config(
    page_title="Power Outages",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Header
st.title("Power Outages")
st.subheader("Geographic Distribution of Power Outages")
st.caption("Visualising UK outage locations aggregated by postcode.")

# Time range toggle
time_window = st.radio(
    "Select Time Range",
    options=["Last 24 Hours", "Last Week"],
    index=0,
    horizontal=True,
)

days_back = 1 if time_window == "Last 24 Hours" else 7

# Sets map display parameters
RADIUS = 600
ELEVATION_SCALE = 50
MAP_STYLE = "mapbox://styles/mapbox/dark-v10"  # ensure dark map tiles

# Fetch data
links_df = fetch_outage_postcodes(days_back=days_back, status=None)
points_df = build_points_from_postcodes(links_df)

if points_df.empty:
    st.warning("No outage locations found in this time range.")
    st.stop()

# Build pydeck map
deck = build_hex_deck(
    points_df,
    radius=RADIUS,
    elevation_scale=ELEVATION_SCALE,
    map_style=MAP_STYLE,
    opacity=0.7,
)

# Force a UK-centred view (balanced around Midlands)
deck.initial_view_state = pdk.ViewState(
    latitude=52.5,
    longitude=-2.5,
    zoom=6,
    pitch=45,
    bearing=0,
)

st.pydeck_chart(deck, use_container_width=True)


sql = "SELECT outage_id, start_time FROM outage WHERE start_time >= now() - interval '7 days';"
df = read_df(sql)

st.subheader("Temporal Patterns in Outages")
st.caption("A heatmap showing when outages most frequently occur across the week.")
st.altair_chart(build_outage_time_heatmap(df), use_container_width=True)


sql = """
SELECT outage_id, start_time, etr
FROM outage
WHERE start_time >= now() - interval '7 days';
"""
df = read_df(sql)

st.subheader("Average Outage Duration by Day")
st.caption(
    "Shows how long outages typically last on each day over the past week.")
st.altair_chart(build_avg_outage_duration_chart(df), use_container_width=True)
