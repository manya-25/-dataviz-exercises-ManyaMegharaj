#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 09:33:35 2026

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
    # Chained filter: Region narrows Country list
    regions = ['All'] + sorted(df['Region'].unique())
    selected_region = st.selectbox("Region", regions)

    if selected_region == 'All':
        country_options = sorted(df['Country'].unique())
    else:
        country_options = sorted(df[df['Region']==selected_region]['Country'].unique())

    selected_countries = st.multiselect("Countries", country_options, default=country_options[:3])
    year_range = st.slider("Year range", int(df['Year'].min()), int(df['Year'].max()), (2000, 2022))

    st.divider()
    # radio: 2-4 exclusive options — clearer than selectbox
    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])

if not selected_countries:
    st.warning("Select at least one country.")
    st.stop()

# applying filtering by country and year range 
filtered = df[
    df['Country'].isin(selected_countries) &
    (df['Year'] >= year_range[0]) &
    (df['Year'] <= year_range[1])
]


y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'
y_label = 'CO2 Emissions (Mt)' if y_col == 'CO2_Mt' else 'CO2 per Capita'

st.caption(f"{len(selected_countries)} countries | {selected_region} | {year_range[0]}–{year_range[1]} | {metric}")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.line(filtered, x='Year', y=y_col, color='Country',
                   labels={y_col: y_label},
                   title=f'{metric} over time')
    
    fig1.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial'))
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    latest = filtered[filtered['Year']==filtered['Year'].max()].sort_values(y_col)
    fig2 = px.bar(latest, x=y_col, y='Country', orientation='h',
                  color_discrete_sequence=['#2E75B6'],  
                  title=f'Latest year ranking - {metric}')
    
    fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white', font=dict(family='Arial'),
                       xaxis=dict(range=[0, latest[y_col].max()*1.15]))
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2)
