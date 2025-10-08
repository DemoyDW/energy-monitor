"""Charting functions for the energy pricing data for the dashboard."""

import pandas as pd
import altair as alt


def build_price_vs_demand_dual_axis(df: pd.DataFrame) -> alt.LayerChart:
    """
    Dual-axis line chart showing demand (MW) and price (£/MWh) with separate scales.
    """
    if df.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No data']})).mark_text().encode(text='msg')

    df = df.copy()
    df['date_time'] = pd.to_datetime(df['date_time'])

    # Demand line
    demand_line = (
        alt.Chart(df)
        .mark_line(color='#ff7675', strokeWidth=2)
        .encode(
            x=alt.X('date_time:T', title='Time'),
            y=alt.Y('demand:Q', title='Demand (MW)',
                    axis=alt.Axis(titleColor='#ff7675')),
            tooltip=['date_time:T', 'demand:Q']
        )
    )

    # Price line (on right axis)
    price_line = (
        alt.Chart(df)
        .mark_line(color='#f1c40f', strokeWidth=2)
        .encode(
            x='date_time:T',
            y=alt.Y('price:Q', title='Price (£/MWh)',
                    axis=alt.Axis(titleColor='#f1c40f')),
            tooltip=['date_time:T', 'price:Q']
        )
    )

    chart = alt.layer(demand_line, price_line).resolve_scale(y='independent')
    return chart.properties(width=700, height=300)


def build_avg_price_by_day_chart(df: pd.DataFrame) -> alt.Chart:
    """
    Bar chart showing average electricity price by day of the week.
    """
    if df.empty:
        return alt.Chart(pd.DataFrame({'msg': ['No data']})).mark_text().encode(text='msg')

    df = df.copy()
    df['date_time'] = pd.to_datetime(df['date_time'])
    df['day_of_week'] = df['date_time'].dt.day_name()

    # Ensure day order
    order = ['Monday', 'Tuesday', 'Wednesday',
             'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Group and average
    avg_price = df.groupby('day_of_week')[
        'price'].mean().reindex(order).reset_index()

    chart = (
        alt.Chart(avg_price)
        .mark_bar(color='#f1c40f', cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X('day_of_week:N', sort=order, title='Day of Week'),
            y=alt.Y('price:Q', title='Average Price (£/MWh)'),
            tooltip=[
                alt.Tooltip('day_of_week:N', title='Day'),
                alt.Tooltip(
                    'price:Q', title='Average Price (£/MWh)', format='.2f')
            ]
        )
        .properties(width=700, height=300)
    )

    return chart
