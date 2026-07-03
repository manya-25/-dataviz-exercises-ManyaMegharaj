#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 09:13:45 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import datetime


# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes

@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("CO₂ Emissions Explorer")

with st.sidebar:
    st.header("Filters")
    
    # filter 1: Multi-select country
    selected_countries = st.multiselect(
        "Countries", sorted(df['Country'].unique()),
        default=['China', 'United States', 'India', 'Germany']
    )
    
    # guard against empty country selection
    if not selected_countries:
        st.warning("Select at least one country.")
        st.stop()
         
    # filter 2 : data range 
    # date_input: use when data has real timestamps (daily/hourly)
    # The CO₂ data has integer years — we converted to dates in the loader
    date_range = st.date_input(
        "Date range",
        value=(datetime.date(2005, 1, 1), datetime.date(2020, 1, 1)),
        min_value=datetime.date(int(df['Year'].min()), 1, 1),
        max_value=datetime.date(int(df['Year'].max()), 1, 1),
        format="YYYY-MM-DD"
    )
    
    # guard against that user may have clicked start but not end yet
    if len(date_range) != 2:
        st.warning("Select a start AND end date.")
        st.stop()

# apply the filtering on countries and date range
#Always convert date → pd.Timestamp before pandas comparisons
start_ts, end_ts = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Date'] >= start_ts) &
    (df['Date'] <= end_ts)
]

# guard against empty filtered data
if filtered.empty:
    st.warning("No data in this date range for the selected countries.")
    st.stop()


# for clarity: showing the number of countries +  the number of data points selected + range of date
st.caption(f"Showing {len(selected_countries)} countries | {len(filtered)} data points")
st.caption(f"{date_range[0].strftime('%d %b %Y')} — {date_range[1].strftime('%d %b %Y')}")


# Figure 1: Line Chart

extended_palette = px.colors.qualitative.Alphabet  # 26 distinct colours
fig = px.line(filtered, x='Date', y='CO2_Mt', color='Country',
              labels={'CO2_Mt': 'CO2 Emissions (Mt)', 'Date': ''},
              color_discrete_sequence=extended_palette)
fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                  font=dict(family='Arial'))
st.plotly_chart(fig, use_container_width=True)


