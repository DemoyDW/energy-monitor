"""Charting and mapping functions for the power outages dashboard."""

from __future__ import annotations
import json
import time
import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import pandas as pd
import requests
import pydeck as pdk
import altair as alt

# Geocoding cache

_CACHE = Path(".cache/postcode_geo.json")
_CACHE.parent.mkdir(parents=True, exist_ok=True)
_BULK_URL = "https://api.postcodes.io/postcodes"


def normalize_postcode(pc: str) -> str:
    return " ".join(str(pc).upper().split()) if pc else pc


def _load_cache() -> Dict[str, Tuple[float, float]]:
    if _CACHE.exists():
        try:
            raw = json.loads(_CACHE.read_text())
            return {k: (float(v[0]), float(v[1])) for k, v in raw.items()}
        except Exception:
            return {}
    return {}


def _save_cache(cache: Dict[str, Tuple[float, float]]):
    _CACHE.write_text(json.dumps({k: [v[0], v[1]] for k, v in cache.items()}))


def _chunks(xs: List[str], n=100):
    for i in range(0, len(xs), n):
        yield xs[i:i+n]


def bulk_lookup_postcodes(postcodes: List[str], sleep_on_429=1.5, max_retries=3) -> Dict[str, Tuple[float, float]]:
    """Call postcodes.io in batches."""
    out: Dict[str, Tuple[float, float]] = {}
    for group in _chunks(postcodes, 100):
        payload = {"postcodes": group}
        for attempt in range(max_retries):
            r = requests.post(_BULK_URL, json=payload, timeout=30)
            if r.status_code == 429 and attempt < max_retries - 1:
                time.sleep(sleep_on_429 * (attempt + 1))
                continue
            r.raise_for_status()
            for item in r.json().get("result", []):
                q = normalize_postcode(item.get("query"))
                res = item.get("result")
                if res:
                    out[q] = (float(res["latitude"]), float(res["longitude"]))
            break
    return out


def geocode_with_cache(postcodes: Iterable[str]) -> Dict[str, Tuple[float, float]]:
    """Return dict {postcode: (lat, lng)} with caching."""
    cache = _load_cache()
    normalized = [normalize_postcode(pc) for pc in postcodes if pc]
    missing = [pc for pc in set(normalized) if pc not in cache]
    if missing:
        resolved = bulk_lookup_postcodes(sorted(missing))
        if resolved:
            cache.update(resolved)
            _save_cache(cache)
    return {pc: cache[pc] for pc in set(normalized) if pc in cache}

# Data shaping


def build_points_from_postcodes(df_links: pd.DataFrame) -> pd.DataFrame:
    """Add lat/lng to outages dataframe."""
    if df_links.empty:
        return pd.DataFrame(columns=["outage_id", "status", "lat", "lng", "weight"])

    df = df_links.copy()
    df["norm"] = df["postcode"].map(normalize_postcode)
    geo = geocode_with_cache(df["norm"].dropna().unique().tolist())

    # postcodes.io returns (latitude, longitude)
    df["lng"] = df["norm"].map(lambda pc: geo.get(pc, (None, None))[1])
    df["lat"] = df["norm"].map(lambda pc: geo.get(pc, (None, None))[0])

    df = df.dropna(subset=["lat", "lng"]).copy()
    df["lat"] = df["lat"].astype(float)
    df["lng"] = df["lng"].astype(float)
    df["weight"] = 1.0
    return df[["outage_id", "status", "postcode", "lat", "lng", "weight"]]


def build_hex_deck(
    df_points: pd.DataFrame,
    radius=600,
    elevation_scale=30,
    map_style="mapbox://styles/mapbox/dark-v10",
    opacity=0.6
):
    """Return a pydeck.Deck object for outage hex map (no tooltips)."""
    if df_points.empty:
        view = pdk.ViewState(latitude=54.5, longitude=-3.0, zoom=5, pitch=45)
        osm = pdk.Layer(
            "TileLayer",
            data="https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
            tile_size=256
        )
        return pdk.Deck(layers=[osm], initial_view_state=view, map_style=None)

    # Compute map centre
    center_lat = float(df_points["lat"].mean()
                       ) if df_points["lat"].notna().any() else 54.5
    center_lng = float(df_points["lng"].mean()
                       ) if df_points["lng"].notna().any() else -3.0

    # Enable Mapbox tiles (fallback to OSM if not set)
    pdk.settings.mapbox_api_key = os.getenv("MAPBOX_API_KEY", "")

    # Camera view
    view = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lng,
        zoom=10,
        pitch=45,
        bearing=0
    )

    # Base OSM tile layer
    osm = pdk.Layer(
        "TileLayer",
        data="https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
        min_zoom=0,
        max_zoom=19,
        tile_size=256
    )

    # Hex layer (aggregated)
    hex_layer = pdk.Layer(
        "HexagonLayer",
        data=df_points,
        get_position='[lng, lat]',
        get_elevation_weight='weight',
        elevation_scale=elevation_scale,
        elevation_range=[0, 4000],
        extruded=True,
        radius=radius,
        coverage=1,
        opacity=opacity,
        color_range=[
            [1, 152, 189],
            [73, 227, 206],
            [216, 254, 181],
            [254, 237, 177],
            [254, 173, 84],
            [209, 55, 78],
        ],
        pickable=False,
    )

    # Scatter points (individual outages)
    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=df_points,
        get_position='[lng, lat]',
        get_radius=250,
        get_fill_color=[255, 255, 255, 160],
        opacity=0.35,
        pickable=False,
        get_line_color=[0, 0, 0],
        line_width_min_pixels=0.5,
        parameters={"depthTest": False}
    )

    # Return Deck without tooltip
    return pdk.Deck(
        layers=[osm, hex_layer, scatter],
        initial_view_state=view,
        map_style=None
    )


def build_outage_time_heatmap(outages_df: pd.DataFrame) -> alt.Chart:
    """
    Build a heatmap showing outage frequency by day of week and hour of day.
    Expects outages_df with a 'start_time' column.
    """
    if outages_df.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No data']})).mark_text().encode(text='msg')

    df = outages_df.copy()
    df['day_of_week'] = pd.to_datetime(df['start_time']).dt.day_name()
    df['hour'] = pd.to_datetime(df['start_time']).dt.hour

    counts = (df.groupby(['day_of_week', 'hour'])
                .size()
                .reset_index(name='outage_count'))

    day_order = ['Monday', 'Tuesday', 'Wednesday',
                 'Thursday', 'Friday', 'Saturday', 'Sunday']

    heatmap = alt.Chart(counts).mark_rect().encode(
        x=alt.X('hour:O', title='Hour of Day'),
        y=alt.Y('day_of_week:O', sort=day_order, title='Day of Week'),
        color=alt.Color('outage_count:Q', scale=alt.Scale(
            scheme='plasma'), title='Outages'),
        tooltip=['day_of_week', 'hour', 'outage_count']
    ).properties(width=600, height=300)

    return heatmap
