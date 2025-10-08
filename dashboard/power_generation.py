"""Streamlit page: Power Generation Overview with time-range filters."""

import streamlit as st
from data import fetch_power_readings
from power_generation_charts import (
    build_generation_mix_chart,
    build_interconnect_chart,
    build_demand_chart,
)

st.set_page_config(page_title="Power Generation", layout="wide")
st.title("Power Generation Overview")
st.caption(
    "Visualising GB's electricity generation, demand, and interconnector flows.")

# Default full dataset (max 7 days)
df_full = fetch_power_readings(days_back=7)

if df_full.empty:
    st.warning("No power generation data found.")
    st.stop()


# Generation Mix Over Time

st.subheader("Generation Mix Over Time")
st.caption(
    "Shows the proportion of energy sources used to generate GB's electricity over time.")

mix_range = st.radio(
    "Select time range for Generation Mix:",
    ["Last 24 Hours", "Last Week"],
    index=1,
    horizontal=True,
)

mix_days_back = 1 if mix_range == "Last 24 Hours" else 7
df_mix = fetch_power_readings(days_back=mix_days_back)

st.altair_chart(build_generation_mix_chart(df_mix), use_container_width=True)


# Total Demand Over Time
st.subheader("Total Demand Over Time")
st.caption("Shows how total grid demand (MW) fluctuates over time.")

demand_range = st.radio(
    "Select time range for Demand:",
    ["Last 24 Hours", "Last Week"],
    index=1,
    horizontal=True,
)

demand_days_back = 1 if demand_range == "Last 24 Hours" else 7
df_demand = fetch_power_readings(days_back=demand_days_back)

st.altair_chart(build_demand_chart(df_demand), use_container_width=True)

# Electricity Imports and Exports by Country
st.subheader("Electricity Imports and Exports by Country")
st.caption("Shows GB's interconnector imports and exports (negative = exports).")

interconnect_range = st.radio(
    "Select time range for Interconnectors:",
    ["Last 24 Hours", "Last Week"],
    index=1,
    horizontal=True,
)

interconnect_days_back = 1 if interconnect_range == "Last 24 Hours" else 7
df_interconnect = fetch_power_readings(days_back=interconnect_days_back)

st.altair_chart(build_interconnect_chart(
    df_interconnect), use_container_width=True)
