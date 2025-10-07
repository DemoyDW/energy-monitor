"""Charting functions for the carbon insights data for the dashboard."""

import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px


@st.cache_data
def create_carbon_intensity_line_graph(df: pd.DataFrame) -> alt.Chart:
    """
    Create a line graph that displays carbon intensity 
    over time for a dataframe of select regions.
    """

    return px.line(df, x='date_time', y='carbon_intensity', color='region_name',
                   labels={"date_time": "Date",
                           "carbon_intensity": "Carbon Intensity gCO2/kWh"}).add_hrect(
        y0=0, y1=29, line_width=0, fillcolor="green", opacity=0.4
    ).add_hrect(
        y0=29, y1=99, line_width=0, fillcolor="green", opacity=0.2
    ).add_hrect(
        y0=99, y1=179, line_width=0, fillcolor="#FFBF00", opacity=0.2
    ).add_hrect(
        y0=179, y1=250, line_width=0, fillcolor="red", opacity=0.2
    ).add_hrect(
        y0=250, y1=300, line_width=0, fillcolor="red", opacity=0.4
    )


@st.cache_data
def create_generation_mix_bar_chart(df: pd.DataFrame, region: str) -> px.bar:
    """Create a bar char of the generation mix for a given region."""

    fuel_types = ["gas", "coal", "biomass", "nuclear",
                  "hydro", "other", "imports", "wind", "solar"]

    df = df.groupby(["region_name"])[fuel_types].mean().round(
        2).transpose().reset_index()

    return px.bar(df, x="index", y=region, title=f"Generation Mix for {region}",
                  labels={
                      "index": "Fuel Type",
                      region: "% Energy Produced"
    })
