"""Charting functions for the power generation data for the dashboard."""

import pandas as pd
import altair as alt


def build_generation_mix_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Stacked area chart showing how each source contributes to total generation.
    Legend and tooltips use capitalised energy source names.
    """
    if df.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No data']})).mark_text().encode(text='msg')

    df = df.copy()
    df['date_time'] = pd.to_datetime(df['date_time'])

    melt_cols = ['gas', 'coal', 'biomass', 'nuclear',
                 'hydro', 'wind', 'solar', 'imports', 'other']
    melted = df.melt(
        id_vars='date_time',
        value_vars=melt_cols,
        var_name='source',
        value_name='generation_mw'
    )

    melted['source_title'] = melted['source'].str.title()

    chart = (
        alt.Chart(melted)
        .mark_area(opacity=0.85)
        .encode(
            x=alt.X('date_time:T', title='Time'),
            y=alt.Y(
                'generation_mw:Q',
                stack='normalize',
                title='Share of Total Generation'
            ),
            color=alt.Color(
                'source_title:N',
                title='Source',
                scale=alt.Scale(scheme='tableau10')
            ),
            tooltip=[
                alt.Tooltip('source_title:N', title='Source'),
                alt.Tooltip('generation_mw:Q',
                            title='Generation (MW)', format=',.0f')
            ]
        )
        .properties(width=700, height=300)
    )

    return chart


def build_interconnect_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Area chart showing electricity imports by interconnector country.
    """
    if df.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No data']})).mark_text().encode(text='msg')

    df = df.copy()
    df['date_time'] = pd.to_datetime(df['date_time'])

    countries = ['france', 'belgium', 'netherlands',
                 'denmark', 'norway', 'ireland', 'n_ireland']
    melted = df.melt(id_vars='date_time', value_vars=countries,
                     var_name='country', value_name='import_mw')

    chart = (
        alt.Chart(melted)
        .mark_area(opacity=0.8)
        .encode(
            x=alt.X('date_time:T', title='Time'),
            y=alt.Y('import_mw:Q', title='Imports (MW)'),
            color=alt.Color('country:N', title='Country',
                            scale=alt.Scale(scheme='category20b')),
            tooltip=['country', 'import_mw']
        )
        .properties(width=700, height=300)
    )
    return chart


def build_demand_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Line chart showing total electricity demand (MW) over time.
    """
    if df.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No data']})).mark_text().encode(text='msg')

    df = df.copy()
    df['date_time'] = pd.to_datetime(df['date_time'])

    chart = (
        alt.Chart(df)
        .mark_line(opacity=0.9, color='#ff7675', strokeWidth=2)
        .encode(
            x=alt.X('date_time:T', title='Time'),
            y=alt.Y('demand:Q', title='Electricity Demand (MW)'),
            tooltip=[
                alt.Tooltip('date_time:T', title='Time'),
                alt.Tooltip('demand:Q', title='Demand (MW)', format=',.0f')
            ]
        )
        .properties(width=700, height=300)
    )

    return chart
