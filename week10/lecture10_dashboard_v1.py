#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 18:50:24 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path



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
          
    
    # filter 2: slider for year range - use when year is cast as an integer
    # Tuple default → two-handle range slider
    year_range = st.slider("Year range",
        int(df['Year'].min()), int(df['Year'].max()), (2010, 2020))
    
    
# applying filtering by country and year range 
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]

# for clarity: showing the number of countries and the number of data points selected
st.caption(f"Showing {len(selected_countries)} countries | {len(filtered)} data points")


# Figure 1: Line chart

extended_palette = px.colors.qualitative.Alphabet  # 26 distinct colours

fig = px.line(filtered, x='Year', y='CO2_Mt', color='Country',
              labels={'CO2_Mt': 'CO2 (Mt)'},
              color_discrete_sequence=extended_palette)
fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                  font=dict(family='Arial'))
st.plotly_chart(fig, use_container_width=True)


### Class exercise: fix the 'too many colors issue here, by using a highlight color only for one country and grey the rest'













