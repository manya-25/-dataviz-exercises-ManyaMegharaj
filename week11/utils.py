# utils.py — shared data loading (imported by every page)
import plotly.express as px
import streamlit as st


@st.cache_data
def load_gapminder():
    # plotly's built-in gapminder dataset: country, continent, year,
    # lifeExp, pop, gdpPercap (+ iso_alpha, iso_num)
    return px.data.gapminder()
