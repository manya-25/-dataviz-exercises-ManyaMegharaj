import streamlit as st
import plotly.express as px
import sys, os

# Streamlit runs each page as its own script, so the project root (where utils.py
# lives) isn't on Python's import path. This adds the parent folder of pages/ to
# sys.path so 'from utils import ...' can find it. Must come before that import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import load_gapminder

df = load_gapminder()
st.header("How do countries compare today?")
st.caption("Bubble = population | Colour = continent")

years = sorted(df['year'].unique())
selected_year = st.selectbox("Year", years, index=len(years) - 1)
df_y = df[df['year'] == selected_year]

c1, c2, c3 = st.columns(3)
c1.metric("Countries", len(df_y))
c2.metric("Avg Life Expectancy", f"{df_y['lifeExp'].mean():.1f} yrs")
c3.metric("Richest country", df_y.loc[df_y['gdpPercap'].idxmax(), 'country'],
          f"${df_y['gdpPercap'].max():,.0f}")
st.divider()


fig = px.scatter(df_y, x='gdpPercap', y='lifeExp', size='pop', color='continent',
                 hover_name='country', log_x=True, size_max=55,
                 labels={'gdpPercap': 'GDP per Capita (log)',
                         'lifeExp': 'Life Expectancy (yrs)'},
                 title=f'Wealthier nations live longer — but diminishing returns '
                       f'above $10,000 ({selected_year})', height=700)
fig.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                  font=dict(family='Arial', size=12))
fig.update_traces(marker=dict(opacity=0.75, line=dict(width=0.5, color='white')))
st.plotly_chart(fig, use_container_width=True)
