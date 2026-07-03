
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="CO2 Dashboard", page_icon="🌱", layout="wide")

# ── Data ──────────────────────────────────────────────────────────────────────
# @st.cache_data: Streamlit reruns the entire script on every widget interaction.
# Without caching, the CSV is read from disk on every interaction — slow and wasteful.
# cache_data stores the result after the first run and reuses it until the file changes.
@st.cache_data
def load_data():
    path = Path(__file__).parent.parent / 'data' / 'co2_emissions.csv'
    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
    return df

df = load_data()

st.title("🌱 CO2 Emissions Explorer")
st.caption("Source: Our World in Data — ourworldindata.org/co2-emissions")

# ── TASK 1: Sidebar with 5 widgets ────────────────────────────────────────────
#   a) st.selectbox for Region (with 'All')
#   b) st.multiselect for Countries (updates based on region — chained)
#   c) st.date_input for date range (two-handle; convert years to Jan-1 dates)
#   d) st.radio for Metric: "Total CO2 (Mt)" vs "CO2 per capita"
#   e) st.checkbox labelled "Show only top emitter highlighted"
#
# Guards:
#   - empty countries → st.warning + st.stop()
#   - incomplete date_input → st.warning + st.stop()
# Convert date_input result to pd.Timestamp before filtering.
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    regions = ['All'] + sorted(df['Region'].dropna().unique().tolist())
    selected_region = st.selectbox("Region", regions)

    if selected_region == 'All':
        country_options = sorted(df['Country'].dropna().unique().tolist())
    else:
        country_options = sorted(
            df.loc[df['Region'] == selected_region, 'Country'].dropna().unique().tolist()
        )

    selected_countries = st.multiselect(
        "Countries",
        country_options,
        default=country_options[:3],
    )

    min_date = pd.Timestamp(df['Date'].min())
    max_date = pd.Timestamp(df['Date'].max())
    date_range = st.date_input(
        "Date range",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

    metric = st.radio("Metric", ["Total CO2 (Mt)", "CO2 per capita"])
    highlight_top = st.checkbox("Show only top emitter highlighted")

if not selected_countries:
    st.warning("Select at least one country.")
    st.stop()

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.warning("Select a complete date range.")
    st.stop()

start_date = pd.Timestamp(date_range[0])
end_date = pd.Timestamp(date_range[1])

y_col = 'CO2_Mt' if metric == "Total CO2 (Mt)" else 'CO2_per_capita'

filtered = df[
    df['Country'].isin(selected_countries)
    & ((selected_region == 'All') | (df['Region'] == selected_region))
    & (df['Date'] >= start_date)
    & (df['Date'] <= end_date)
].copy()

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

filtered = filtered.sort_values(['Country', 'Date'])


# ── TASK 2: Filter summary caption ────────────────────────────────────────────
# Show: "X countries | Region | Date range | Metric"
# BBD rule: always show users how many records match current filters
# ─────────────────────────────────────────────────────────────────────────────
st.caption(
    f"{len(filtered):,} records | {len(selected_countries)} countries | {selected_region} | "
    f"{start_date.year}–{end_date.year} | {metric}"
)


# ── EXTENSION: KPI row above the charts ───────────────────────────────────────
selected_years = sorted(filtered['Year'].unique().tolist())
first_year = selected_years[0]
last_year = selected_years[-1]
first_year_total = filtered.loc[filtered['Year'] == first_year, y_col].sum()
last_year_total = filtered.loc[filtered['Year'] == last_year, y_col].sum()
highest_last_year = filtered.loc[filtered['Year'] == last_year].sort_values(y_col, ascending=False).iloc[0]
if first_year_total:
    pct_change = (last_year_total - first_year_total) / first_year_total
    delta_text = f"{pct_change:+.1%}"
else:
    delta_text = "n/a"

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(f"{metric} in {last_year}", f"{last_year_total:,.1f}")
kpi2.metric(f"Change since {first_year}", delta_text)
kpi3.metric(f"Highest emitter in {last_year}", highest_last_year['Country'])


# ── TASK 3: Two charts reacting to ALL filters ────────────────────────────────
#   Left: line chart — selected metric over time, one line per country
#         If "Show only top emitter highlighted" checkbox is on:
#           - grey all lines except the highest emitter in the date range
#           - label that country at the end of its line (SWD grey-and-highlight)
#   Right: bar chart — ranking for the last year in selected date range
#
# BBD colour requirement: name the colour type in a comment next to each chart
# SWD requirements: white background, insight title, use_container_width=True
# ─────────────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # Line chart
    # BBD COLOUR TYPE: categorical — each country gets a distinct hue unless highlighted
    st.subheader(f"{metric} over time")

    line_fig = px.line(
        filtered,
        x='Date',
        y=y_col,
        color='Country',
        labels={'Date': '', y_col: metric, 'Country': ''},
    )

    if highlight_top:
        highlight_country = (
            filtered.groupby('Country', as_index=False)[y_col]
            .sum()
            .sort_values(y_col, ascending=False)
            .iloc[0]['Country']
        )

        for trace in line_fig.data:
            if trace.name == highlight_country:
                trace.update(
                    line=dict(color='#2E75B6', width=3.5),
                    mode='lines+markers+text',
                    text=[None] * (len(trace.x) - 1) + [trace.name],
                    textposition='top right',
                    textfont=dict(color='#2E75B6', size=12),
                )
            else:
                trace.update(
                    line=dict(color='#D0D0D0', width=1.5),
                    opacity=0.7,
                    mode='lines',
                    showlegend=False,
                )

    line_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend_title_text='',
        xaxis=dict(gridcolor='#EEEEEE'),
        yaxis=dict(gridcolor='#EEEEEE'),
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    st.plotly_chart(line_fig, use_container_width=True)

with col_right:
    # Bar chart
    # BBD COLOUR TYPE: sequential — ordered ranking shown with a single strong hue
    st.subheader(f"Ranking in {last_year}")

    latest = filtered.loc[filtered['Year'] == last_year].sort_values(y_col, ascending=True)
    bar_fig = px.bar(
        latest,
        x=y_col,
        y='Country',
        orientation='h',
        color_discrete_sequence=['#2E75B6'],
        labels={y_col: metric, 'Country': ''},
        title=f"{metric} ranking in {last_year}",
    )

    bar_fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='#EEEEEE'),
        yaxis=dict(gridcolor='#EEEEEE'),
        font=dict(family='Arial', size=12),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    bar_fig.update_traces(marker_line_width=0)
    st.plotly_chart(bar_fig, use_container_width=True)