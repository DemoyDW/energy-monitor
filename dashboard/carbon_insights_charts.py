"""Charting functions for the carbon insights data for the dashboard."""

from shapely.geometry import mapping
import geopandas as gpd
import json
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
                           "carbon_intensity": "Carbon Intensity gCO2/kWh",
                           "region_name": "Region Name"}).add_hrect(
        y0=0, y1=29, line_width=0, fillcolor="green", opacity=0.4
    ).add_hrect(
        y0=29, y1=99, line_width=0, fillcolor="green", opacity=0.2
    ).add_hrect(
        y0=99, y1=179, line_width=0, fillcolor="#FFBF00", opacity=0.2
    ).add_hrect(
        y0=179, y1=250, line_width=0, fillcolor="red", opacity=0.2
    ).add_hrect(
        y0=250, y1=400, line_width=0, fillcolor="red", opacity=0.4
    )


@st.cache_data
def create_generation_mix_bar_chart(df: pd.DataFrame, region: str) -> px.bar:
    """Create a bar char of the generation mix for a given region."""

    fuel_types = ["gas", "coal", "biomass", "nuclear",
                  "hydro", "other", "imports", "wind", "solar"]

    df = df.groupby(["region_name"])[fuel_types].mean().round(
        2).transpose().reset_index()
    df["index"] = df["index"].str.capitalize()

    return px.bar(df, x="index", y=region, title=f"Generation Mix for {region}",
                  labels={
                      "index": "Fuel Type",
                      region: "% Energy Produced"
    })


@st.cache_data(show_spinner=False)
def prepare_choropleth_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate average carbon intensity per region and normalise names."""
    df = df.copy()
    df["region_name"] = (
        df["region_name"]
        .str.strip()
        .replace({"Gb": "GB"})
        .str.title()
    )
    df["region_name"] = df["region_name"].replace({"Gb": "GB", "Gb ": "GB"})
    df["date_time"] = pd.to_datetime(df["date_time"])
    grouped = (
        df.groupby("region_name", as_index=False)["carbon_intensity"]
        .mean()
        .round(1)
    )
    return grouped


def create_carbon_heatmap(df: pd.DataFrame):
    """Visualise carbon intensity by region using simple map tiles."""

    #  Removes Wales from the map.
    df = df[~df["region_name"].isin(
        ["Wales", "England", "Scotland", "GB"])].copy()

    # Approximate centroids for each region
    coords = {
        "North Scotland": (58.5, -4.5),
        "South Scotland": (56, -3.5),
        "North West England": (54.5, -3),
        "North East England": (54.5, -1.5),
        "Yorkshire": (53.8, -1.2),
        "North Wales & Merseyside": (53, -3.5),
        "South Wales": (51.8, -3.2),
        "West Midlands": (52.5, -2.1),
        "East Midlands": (52.8, -1.2),
        "East England": (52.2, 1),
        "South West England": (51, -3.5),
        "South England": (51.2, -1.5),
        "London": (51.5, -0.1),
        "South East England": (51.3, 0.8)
    }

    df["lat"] = df["region_name"].map(lambda x: coords.get(x, (60, -3.5))[0])
    df["lon"] = df["region_name"].map(lambda x: coords.get(x, (60, -3.5))[1])

    hover_data = {
        "carbon_intensity": True,
        "lat": False,
        "lon": False
    }

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="carbon_intensity",
        size="carbon_intensity",
        center={"lat": 54.8, "lon": -3.5},
        color_continuous_scale="RdYlGn_r",
        size_max=40,
        zoom=4,
        mapbox_style="carto-darkmatter",
        hover_name="region_name",
        hover_data=hover_data,
        labels={"carbon_intensity": "Carbon Intensity (gCO₂/kWh)"},
    )

    fig.update_traces(marker=dict(size=25))

    fig.update_layout(
        margin=dict(r=0, t=40, l=0, b=0),
        coloraxis_colorbar=dict(title="gCO₂/kWh")
    )
    return fig
