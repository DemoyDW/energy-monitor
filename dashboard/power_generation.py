"""Script to display the power generation data on the Streamlit dashboard."""

import streamlit as st
from data import fetch_power_readings
from power_generation_charts import (
    build_generation_mix_chart, build_interconnect_chart, build_demand_chart
)

st.set_page_config(page_title="Power Generation", layout="wide")
st.title("Power Generation Overview")
st.caption(
    "Visualising GB's electricity generation, demand, and interconnector flows.")

# Data fetch
df = fetch_power_readings(days_back=7)

if df.empty:
    st.warning("No power generation data found.")
    st.stop()

# Layout
st.subheader("Generation Mix Over Time")
st.caption(
    "Shows the proportion of energy sources used to generate GB's energy over time.")
st.altair_chart(build_generation_mix_chart(df), use_container_width=True)

st.subheader("Total Demand Over Time")
st.caption("Shows how total grid demand (in MW) fluctuates over time.")
st.altair_chart(build_demand_chart(df), use_container_width=True)

st.subheader("Electricity Imports and Exports by Country.")
st.caption("Shows GB's energy imports and exports (negative import values on the graph) to other countries around Europe.")
st.altair_chart(build_interconnect_chart(df), use_container_width=True)
