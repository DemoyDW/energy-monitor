"""Script to display the energy pricing data on the Streamlit dashboard."""

import streamlit as st
from data import fetch_energy_prices
from energy_prices_charts import (
    build_price_vs_demand_dual_axis,
    build_avg_price_by_day_chart
)

st.set_page_config(page_title="Energy Prices", layout="wide")
st.title("Energy Prices")
st.caption(
    "Analysing how UK electricity prices relate to demand and vary by day of week.")

# Fetch recent data
df = fetch_energy_prices(days_back=7)

if df.empty:
    st.warning("No price data found.")
    st.stop()

st.subheader("Price vs Demand")
st.caption("Shows how price (£/MWh) tracks changes in grid demand (MW) over time.")
st.altair_chart(build_price_vs_demand_dual_axis(df), use_container_width=True)

st.subheader("Average Price by Day of Week")
st.caption("Highlights typical daily trends in average market price.")
st.altair_chart(build_avg_price_by_day_chart(df), use_container_width=True)
