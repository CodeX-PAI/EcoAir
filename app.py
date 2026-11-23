import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# EcoAir | Air Quality Analytics Dashboard
# Sources:
#   OpenAQ      -> sensor/station measurements stored in SQLite
#   Open-Meteo -> model-based air-quality estimates from CSV
# =========================================================

st.set_page_config(
    page_title="EcoAir | Air Quality Tracker",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Project directory
BASE_DIR = Path(__file__).resolve().parent

# Data file paths
DB_FILE = BASE_DIR / "air_quality.db"
OPENMETEO_FILE = BASE_DIR / "CSV datasets" / "air_quality_openmeteo_raw.csv"

COLORS = {
    "green": "#16A34A",
    "yellow": "#EAB308",
    "red": "#DC2626",
    "blue": "#2563EB",
    "purple": "#9333EA",
    "teal": "#0D9488",
    "orange": "#EA580C",
    "ink": "#172033",
    "muted": "#64748B",
    "bg": "#F4F7FB",
}

POLLUTANT_COLORS = {
    "pm25": COLORS["red"],
    "pm2_5": COLORS["red"],
    "pm10": COLORS["orange"],
    "ozone": COLORS["purple"],
    "nitrogen_dioxide": COLORS["blue"],
    "sulphur_dioxide": COLORS["yellow"],
    "carbon_dioxide": COLORS["teal"],
    "temperature": COLORS["orange"],
    "relativehumidity": COLORS["blue"],
}


# -------------------- Styling --------------------

st.markdown(
    f"""
    <style>

    /* =========================================
       MAIN APPLICATION BACKGROUND
    ========================================= */

    .stApp {{
        background: linear-gradient(
            145deg,
            #F4F7FB 0%,
            #EEF3FA 55%,
            #F7F2FF 100%
        );
        color: {COLORS["ink"]};
    }}

    /* =========================================
       SIDEBAR BACKGROUND
    ========================================= */

    [data-testid="stSidebar"] {{
        background: linear-gradient(
            180deg,
            #172033 0%,
            #24324B 65%,
            #30254B 100%
        );
    }}

    /* Default sidebar text */
    [data-testid="stSidebar"] * {{
        color: #F8FAFC !important;
    }}

    /* Sidebar labels */
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stDateInput label {{
        color: #E2E8F0 !important;
    }}

    /* =========================================
       SIDEBAR DROPDOWN FIELDS
    ========================================= */

    [data-testid="stSidebar"] [data-baseweb="select"] {{
        background-color: #FFFFFF !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div {{
        color: #1E293B !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        color: #64748B !important;
        fill: #64748B !important;
    }}

    /* =========================================
       DATE RANGE - ACTUAL TEXT VISIBILITY FIX
       Targets the start/end elements identified
       in the browser developer tools.
    ========================================= */

    [data-testid="stSidebar"] .st-key-openaq_date_range
    [data-range-field="start"],

    [data-testid="stSidebar"] .st-key-openaq_date_range
    [data-range-field="end"],

    [data-testid="stSidebar"] .st-key-openaq_date_range
    [data-range-field="start"] *,

    [data-testid="stSidebar"] .st-key-openaq_date_range
    [data-range-field="end"] * {{
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        opacity: 1 !important;
        font-weight: 700 !important;
    }}

    /* Date range field backgrounds */
    [data-testid="stSidebar"] .st-key-openaq_date_range
    [data-range-field="start"],

    [data-testid="stSidebar"] .st-key-openaq_date_range
    [data-range-field="end"] {{
        background-color: #FFFFFF !important;
    }}

    /* Date range container */
    [data-testid="stSidebar"] .st-key-openaq_date_range
    [data-baseweb="input"] {{
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 9px !important;
    }}

    /* Date range calendar icon */
    [data-testid="stSidebar"] .st-key-openaq_date_range svg {{
        color: #475569 !important;
        fill: #475569 !important;
    }}

    /* Date input fields, if rendered as inputs */
    [data-testid="stSidebar"] .st-key-openaq_date_range input {{
        background-color: #FFFFFF !important;
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        opacity: 1 !important;
        font-weight: 700 !important;
    }}

    /* =========================================
       OTHER SIDEBAR INPUTS
    ========================================= */

    [data-testid="stSidebar"] input {{
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        -webkit-text-fill-color: #1E293B !important;
    }}

    [data-testid="stSidebar"] [data-baseweb="input"] {{
        background-color: #FFFFFF !important;
    }}

    /* =========================================
       MAIN CONTENT SPACING
    ========================================= */

    .block-container {{
        padding-top: 1.6rem;
        padding-bottom: 2.4rem;
        max-width: 1600px;
    }}

    /* =========================================
       HEADINGS
    ========================================= */

    h1, h2, h3 {{
        letter-spacing: -0.025em;
    }}

    h1 {{
        color: #172033 !important;
        font-weight: 850 !important;
    }}

    h2, h3 {{
        color: #273858 !important;
    }}

    /* =========================================
       METRIC CARDS
    ========================================= */

    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.92);
        border: 1px solid #DCE5F0;
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 7px 22px rgba(30, 50, 80, 0.06);
    }}

    [data-testid="stMetricLabel"] {{
        color: #64748B !important;
        font-weight: 650 !important;
    }}

    [data-testid="stMetricValue"] {{
        color: #172033 !important;
        font-weight: 850 !important;
    }}

    /* =========================================
       PLOTLY CHARTS
    ========================================= */

    div[data-testid="stPlotlyChart"] {{
        background: #FFFFFF;
        border: 1px solid #E1E8F0;
        border-radius: 16px;
        padding: 8px;
        box-shadow: 0 6px 20px rgba(30,50,80,0.04);
    }}

    /* =========================================
       DATA TABLES
    ========================================= */

    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E1E8F0;
    }}

    /* =========================================
       TABS
    ========================================= */

    div[data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    button[data-baseweb="tab"] {{
        border-radius: 10px 10px 0 0;
        padding: 12px 16px;
        font-weight: 650;
    }}

    /* =========================================
       FILTER TAGS
    ========================================= */

    [data-baseweb="tag"] {{
        background-color: #E7EEFF !important;
        border: 1px solid #C5D5FF !important;
        border-radius: 8px !important;
    }}

    [data-baseweb="tag"] span {{
        color: #244B9A !important;
    }}

    /* =========================================
       HERO BANNER
    ========================================= */

    .eco-hero {{
        background: linear-gradient(
            120deg,
            #172033 0%,
            #263A5C 55%,
            #45336C 100%
        );
        border-radius: 22px;
        padding: 26px 28px;
        color: white;
        margin-bottom: 14px;
        box-shadow: 0 12px 28px rgba(25, 40, 70, 0.15);
    }}

    .eco-hero h2 {{
        color: white !important;
        margin: 0 0 6px 0;
        font-size: 1.8rem;
    }}

    .eco-hero p {{
        color: #D8E4F5;
        margin: 0;
    }}

    /* =========================================
       HERO CHIPS
    ========================================= */

    .eco-chip {{
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 750;
        margin: 3px 4px 3px 0;
        background: rgba(255,255,255,0.13);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
    }}

    /* =========================================
       SOURCE INFORMATION BOXES
    ========================================= */

    .source-box {{
        border-radius: 14px;
        padding: 15px 17px;
        margin: 4px 0 12px 0;
        border: 1px solid #DCE5F0;
        background: #FFFFFF;
        color: #1E293B;
    }}

    .small-note {{
        color: #64748B;
        font-size: 0.88rem;
    }}

    /* =========================================
       ALERTS
    ========================================= */

    div[data-testid="stAlert"] {{
        border-radius: 12px;
    }}

    /* =========================================
       DIVIDERS
    ========================================= */

    hr {{
        border-color: #DCE5F0;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- Styling End --------------------

# -------------------- Helpers --------------------
def empty_message(message: str):
    st.info(message)

def load_openaq():
    if not Path(DB_FILE).exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_FILE)
    try:
        data = pd.read_sql_query("SELECT * FROM measurements", conn)
    finally:
        conn.close()
    if data.empty:
        return data
    for col in ("datetime_utc", "datetime_local"):
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce", utc=True)
    if "value" in data.columns:
        data["value"] = pd.to_numeric(data["value"], errors="coerce")
    return data

def load_openmeteo():
    if not Path(OPENMETEO_FILE).exists():
        return pd.DataFrame()
    data = pd.read_csv(OPENMETEO_FILE)
    if data.empty:
        return data
    if "time" in data.columns:
        raw_time = data["time"]
        if pd.api.types.is_numeric_dtype(raw_time):
            data["time"] = pd.to_datetime(raw_time, unit="s", errors="coerce", utc=True)
        else:
            data["time"] = pd.to_datetime(raw_time, errors="coerce", utc=True)
    for col in data.columns:
        if col not in ("time", "source", "fetched_at_utc"):
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data

def nice_parameter(param):
    return str(param).replace("_", " ").upper()

def plot_theme(fig, height=420):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=15, r=15, t=65, b=15),
        font=dict(family="Arial", color=COLORS["ink"]),
        title=dict(font=dict(size=18, color=COLORS["ink"])),
        legend_title_text="",
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#E9EEF5", zeroline=False)
    return fig

def color_for_parameter(param):
    return POLLUTANT_COLORS.get(str(param).lower(), COLORS["teal"])

def date_bounds(data, date_column):
    valid = data[date_column].dropna()
    if valid.empty:
        today = pd.Timestamp.now().date()
        return today, today
    return valid.min().date(), valid.max().date()

# -------------------- Load both datasets --------------------
with st.spinner("Loading EcoAir datasets..."):
    try:
        aq_df = load_openaq()
    except Exception as exc:
        aq_df = pd.DataFrame()
        st.error(f"Could not load OpenAQ database: {exc}")

    try:
        meteo_df = load_openmeteo()
    except Exception as exc:
        meteo_df = pd.DataFrame()
        st.warning(f"Could not load Open-Meteo CSV: {exc}")

# -------------------- Header --------------------
st.markdown(
    """
    <div class="eco-hero">
        <h2>🌿 EcoAir — Air Quality Intelligence</h2>
        <p>Explore Lahore air quality through station measurements, hourly pollutant trends,
        statistical summaries, and model-based atmospheric estimates.</p>
        <span class="eco-chip">🔵 OpenAQ · Station data</span>
        <span class="eco-chip">🟣 Open-Meteo · Model estimates</span>
        <span class="eco-chip">🟢 Interactive analytics</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Educational analytics dashboard · Values are presented with their source and units. This is not an official health advisory.")

# -------------------- Sidebar controls --------------------
st.sidebar.markdown("## 🎛️ Dashboard Controls")
st.sidebar.markdown("Filter the station dataset for the views below.")

if aq_df.empty:
    st.sidebar.warning("OpenAQ data is unavailable.")
    stations = []
    parameters = []
else:
    stations = sorted(aq_df["location_name"].dropna().unique())
    parameters = sorted(aq_df["parameter"].dropna().unique())

selected_station = st.sidebar.selectbox("Monitoring station", ["All stations"] + stations)
default_param = parameters.index("pm25") if "pm25" in parameters else 0
selected_parameter = st.sidebar.selectbox("OpenAQ pollutant / parameter", parameters, index=default_param) if parameters else None

# Date range for OpenAQ
if not aq_df.empty and "datetime_utc" in aq_df.columns:
    min_date, max_date = date_bounds(aq_df, "datetime_utc")
    date_range = st.sidebar.date_input(
        "OpenAQ date range (UTC)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="openaq_date_range",
        format="YYYY/MM/DD",
    )
else:
    date_range = None

# Build OpenAQ filters
aq_filtered = aq_df.copy()
if not aq_filtered.empty and selected_parameter:
    aq_filtered = aq_filtered[aq_filtered["parameter"] == selected_parameter]
if not aq_filtered.empty and selected_station != "All stations":
    aq_filtered = aq_filtered[aq_filtered["location_name"] == selected_station]
if not aq_filtered.empty and date_range and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    start_ts = pd.Timestamp(start_date, tz="UTC")
    end_ts = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    aq_filtered = aq_filtered[
        aq_filtered["datetime_utc"].between(start_ts, end_ts, inclusive="both")
    ]
if not aq_filtered.empty:
    aq_filtered = aq_filtered.sort_values("datetime_utc")

# -------------------- Global KPIs --------------------
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("📍 Monitoring stations", aq_df["location_name"].nunique() if not aq_df.empty else 0)
with k2:
    st.metric("🔵 OpenAQ records", f"{len(aq_df):,}")
with k3:
    st.metric("🟣 Open-Meteo records", f"{len(meteo_df):,}")
with k4:
    pollutant_count = len([p for p in parameters if p]) if parameters else 0
    st.metric("🧪 OpenAQ parameters", pollutant_count)

# -------------------- Tabs --------------------
overview_tab, aq_tab, meteo_tab, compare_tab, explorer_tab = st.tabs(
    ["✨ Overview", "🔵 OpenAQ Trends", "🟣 Open-Meteo", "📊 Compare Stations", "🗂️ Data Explorer"]
)

# ========== OVERVIEW ==========
with overview_tab:
    st.subheader("Overview & Snapshot")
    left, right = st.columns([1.3, 1])
    with left:
        if aq_filtered.empty:
            empty_message("No OpenAQ readings match the current sidebar filters.")
        else:
            avg_val = aq_filtered["value"].mean()
            min_val = aq_filtered["value"].min()
            max_val = aq_filtered["value"].max()
            unit = aq_filtered["unit"].dropna().iloc[0] if "unit" in aq_filtered and not aq_filtered["unit"].dropna().empty else ""
            latest = aq_filtered.sort_values("datetime_utc").iloc[-1]
            latest_dt = latest["datetime_utc"]
            param_color = color_for_parameter(selected_parameter)

            st.markdown(
                f"""
                <div class="source-box" style="border-left: 7px solid {param_color};">
                    <div style="font-size:0.82rem;color:#64748B;font-weight:700;">SELECTED OPENAQ PARAMETER</div>
                    <div style="font-size:1.7rem;font-weight:850;color:#172033;">{nice_parameter(selected_parameter)}</div>
                    <div style="font-size:1rem;color:#475569;">{selected_station}</div>
                    <div style="font-size:1.2rem;font-weight:750;color:{param_color};margin-top:7px;">Mean: {avg_val:.2f} {unit}</div>
                    <div style="font-size:0.86rem;color:#64748B;">Latest record in filtered data: {latest_dt.strftime("%d %b %Y, %H:%M UTC")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            m1, m2, m3 = st.columns(3)
            m1.metric("Average", f"{avg_val:.2f} {unit}")
            m2.metric("Minimum", f"{min_val:.2f} {unit}")
            m3.metric("Maximum", f"{max_val:.2f} {unit}")

    with right:
        if not aq_filtered.empty:
            counts = aq_filtered.groupby("location_name").size().reset_index(name="Records")
            pie = px.pie(
                counts,
                names="location_name",
                values="Records",
                hole=0.58,
                title="Filtered records by station",
                color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["yellow"], COLORS["purple"], COLORS["red"]],
            )
            plot_theme(pie, 330)
            pie.update_traces(textposition="inside", textinfo="label+percent")
            st.plotly_chart(pie, use_container_width=True)
        elif not aq_df.empty:
            empty_message("Select a valid filter to display station distribution.")

    if not aq_filtered.empty:
        st.subheader("📈 Station readings through time")
        trend = px.line(
            aq_filtered,
            x="datetime_utc",
            y="value",
            color="location_name",
            markers=True,
            title=f"{nice_parameter(selected_parameter)} — filtered station readings",
            labels={"datetime_utc": "Time (UTC)", "value": "Reading", "location_name": "Station"},
            color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"], COLORS["red"]],
        )
        plot_theme(trend, 430)
        trend.update_traces(line_width=2.5, marker_size=5)
        st.plotly_chart(trend, use_container_width=True)

    st.markdown("#### Data-source guide")
    src1, src2 = st.columns(2)
    with src1:
        st.markdown(
            f"""<div class="source-box" style="border-left:6px solid {COLORS["blue"]}">
            <b>🔵 OpenAQ — Station measurements</b><br>
            Sensor observations collected at individual monitoring locations and stored in the project's SQLite database.
            </div>""",
            unsafe_allow_html=True,
        )
    with src2:
        st.markdown(
            f"""<div class="source-box" style="border-left:6px solid {COLORS["purple"]}">
            <b>🟣 Open-Meteo — Model-based estimates</b><br>
            Hourly air-quality model output for the configured Lahore coordinates, saved separately as CSV.
            </div>""",
            unsafe_allow_html=True,
        )

# ========== OPENAQ TRENDS ==========
with aq_tab:
    st.subheader("🔵 OpenAQ — Sensor Dataset")
    if aq_filtered.empty:
        empty_message("No OpenAQ measurements available for these filters.")
    else:
        unit = aq_filtered["unit"].dropna().iloc[0] if "unit" in aq_filtered and not aq_filtered["unit"].dropna().empty else ""
        chart_choice = st.radio("Chart style", ["Line chart", "Area chart", "Box plot"], horizontal=True, key="aq_chart_style")
        if chart_choice == "Line chart":
            fig = px.line(
                aq_filtered, x="datetime_utc", y="value", color="location_name", markers=True,
                title=f"{nice_parameter(selected_parameter)} over time",
                labels={"datetime_utc": "Time (UTC)", "value": f"Value ({unit})", "location_name": "Station"},
                color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"], COLORS["red"]],
            )
        elif chart_choice == "Area chart":
            fig = px.area(
                aq_filtered, x="datetime_utc", y="value", color="location_name",
                title=f"{nice_parameter(selected_parameter)} area trend",
                labels={"datetime_utc": "Time (UTC)", "value": f"Value ({unit})", "location_name": "Station"},
                color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"], COLORS["red"]],
            )
        else:
            fig = px.box(
                aq_filtered, x="location_name", y="value", color="location_name", points="all",
                title=f"{nice_parameter(selected_parameter)} distribution by station",
                labels={"location_name": "Station", "value": f"Value ({unit})"},
                color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"], COLORS["red"]],
            )
        plot_theme(fig, 460)
        st.plotly_chart(fig, use_container_width=True)

        if selected_station == "All stations":
            st.subheader("Station average comparison")
            avg_station = aq_filtered.groupby("location_name", as_index=False)["value"].mean().sort_values("value", ascending=False)
            bar = px.bar(
                avg_station, x="location_name", y="value", color="location_name", text_auto=".2f",
                title=f"Mean {nice_parameter(selected_parameter)} by station",
                labels={"location_name": "Station", "value": f"Mean ({unit})"},
                color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"], COLORS["red"]],
            )
            plot_theme(bar, 380)
            bar.update_layout(showlegend=False)
            st.plotly_chart(bar, use_container_width=True)

        st.subheader("Summary statistics")
        stats = aq_filtered.groupby("location_name")["value"].agg(["count", "mean", "median", "min", "max", "std"]).round(2)
        stats.columns = ["Records", "Mean", "Median", "Minimum", "Maximum", "Std. Dev."]
        st.dataframe(stats, use_container_width=True)

# ========== OPEN-METEO ==========
with meteo_tab:
    st.subheader("🟣 Open-Meteo — Model-based air quality")
    st.markdown(
        "These values are **model-based estimates**, not direct readings from the OpenAQ station sensors.",
        unsafe_allow_html=True,
    )
    if meteo_df.empty:
        st.warning(f"Open-Meteo dataset not found. Run `extract_openmeteo.py` to create `{OPENMETEO_FILE}`.")
    else:
        meteo_params = [c for c in ["pm10", "pm2_5", "ozone", "nitrogen_dioxide", "sulphur_dioxide", "carbon_dioxide"] if c in meteo_df.columns]
        chosen_meteo = st.selectbox("Select Open-Meteo pollutant", meteo_params, index=meteo_params.index("pm2_5") if "pm2_5" in meteo_params else 0)
        meteo_chart_type = st.radio("Visualization", ["Hourly trend", "Distribution", "Compare pollutants"], horizontal=True, key="meteo_chart_type")
        color = color_for_parameter(chosen_meteo)
        if meteo_chart_type == "Hourly trend":
            meteo_plot = meteo_df.dropna(subset=["time", chosen_meteo]).sort_values("time")
            fig = px.line(
                meteo_plot, x="time", y=chosen_meteo, markers=True,
                title=f"Lahore {nice_parameter(chosen_meteo)} hourly trend — Open-Meteo",
                labels={"time": "Time", chosen_meteo: "Concentration / value"},
            )
            fig.update_traces(line_color=color, marker_color=color, line_width=3)
        elif meteo_chart_type == "Distribution":
            meteo_plot = meteo_df.dropna(subset=[chosen_meteo])
            fig = px.histogram(
                meteo_plot, x=chosen_meteo, nbins=30,
                title=f"Distribution of {nice_parameter(chosen_meteo)}",
                labels={chosen_meteo: "Value"},
            )
            fig.update_traces(marker_color=color)
        else:
            compare_cols = st.multiselect("Pollutants to compare", meteo_params, default=meteo_params[:4], key="meteo_compare_cols")
            if not compare_cols:
                st.info("Choose at least one pollutant.")
                fig = None
            else:
                # Normalize to 0–1 to make pollutants with different scales comparable.
                normalized = meteo_df[["time"] + compare_cols].copy()
                for col in compare_cols:
                    low, high = normalized[col].min(), normalized[col].max()
                    normalized[col] = (normalized[col] - low) / (high - low) if pd.notna(low) and pd.notna(high) and high != low else 0
                melted = normalized.melt(id_vars="time", var_name="Pollutant", value_name="Normalized value")
                fig = px.line(
                    melted, x="time", y="Normalized value", color="Pollutant",
                    title="Normalized pollutant trends (0–1 scale)",
                    color_discrete_sequence=[COLORS["red"], COLORS["orange"], COLORS["purple"], COLORS["blue"], COLORS["yellow"], COLORS["teal"]],
                )
        if fig is not None:
            plot_theme(fig, 450)
            st.plotly_chart(fig, use_container_width=True)

        selected_values = meteo_df[chosen_meteo].dropna()
        if not selected_values.empty:
            a, b, c, d = st.columns(4)
            a.metric("Average", f"{selected_values.mean():.2f}")
            b.metric("Minimum", f"{selected_values.min():.2f}")
            c.metric("Maximum", f"{selected_values.max():.2f}")
            d.metric("Available observations", f"{len(selected_values):,}")
        st.subheader("Open-Meteo pollutant statistics")
        meteo_stats = meteo_df[meteo_params].describe().T.round(2)
        st.dataframe(meteo_stats, use_container_width=True)

# ========== COMPARE STATIONS ==========
with compare_tab:
    st.subheader("📊 Multi-station comparison")
    if aq_df.empty:
        empty_message("OpenAQ data is unavailable.")
    else:
        comp_param = st.selectbox("Parameter for comparison", parameters, index=default_param, key="compare_param")
        comp_df = aq_df[aq_df["parameter"] == comp_param].copy()
        if comp_df.empty:
            empty_message("No records for the chosen parameter.")
        else:
            compare_mode = st.radio("Comparison view", ["Average", "Minimum / maximum range", "Distribution"], horizontal=True)
            if compare_mode == "Average":
                values = comp_df.groupby("location_name", as_index=False)["value"].mean().sort_values("value", ascending=False)
                fig = px.bar(
                    values, x="location_name", y="value", color="location_name", text_auto=".2f",
                    title=f"Mean {nice_parameter(comp_param)} across stations",
                    color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"], COLORS["red"]],
                )
            elif compare_mode == "Minimum / maximum range":
                values = comp_df.groupby("location_name")["value"].agg(["mean", "min", "max"]).reset_index()
                fig = go.Figure()
                for i, row in values.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row["location_name"], row["location_name"]],
                        y=[row["min"], row["max"]],
                        mode="lines",
                        line=dict(color=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"]][i % 4], width=9),
                        name=f'{row["location_name"]} range',
                    ))
                    fig.add_trace(go.Scatter(
                        x=[row["location_name"]], y=[row["mean"]], mode="markers",
                        marker=dict(size=13, color=COLORS["red"], symbol="diamond"),
                        name=f'{row["location_name"]} mean',
                    ))
                fig.update_layout(title=f"{nice_parameter(comp_param)} range and mean by station", yaxis_title="Value")
            else:
                fig = px.box(
                    comp_df, x="location_name", y="value", color="location_name", points="outliers",
                    title=f"{nice_parameter(comp_param)} distribution by station",
                    color_discrete_sequence=[COLORS["green"], COLORS["blue"], COLORS["purple"], COLORS["orange"], COLORS["red"]],
                )
            plot_theme(fig, 440)
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("Station comparison table")
            summary = comp_df.groupby("location_name")["value"].agg(["count", "mean", "median", "min", "max", "std"]).round(2)
            summary.columns = ["Records", "Mean", "Median", "Minimum", "Maximum", "Std. Dev."]
            st.dataframe(summary, use_container_width=True)

# ========== DATA EXPLORER ==========
with explorer_tab:
    st.subheader("🗂️ Data Explorer & Downloads")
    source_choice = st.radio("Dataset", ["OpenAQ database", "Open-Meteo CSV"], horizontal=True)
    if source_choice == "OpenAQ database":
        if aq_df.empty:
            empty_message("OpenAQ data is unavailable.")
        else:
            explorer = aq_df.copy()
            station_options = sorted(explorer["location_name"].dropna().unique())
            parameter_options = sorted(explorer["parameter"].dropna().unique())
            chosen_stations = st.multiselect("Stations", station_options, default=station_options, key="explorer_stations")
            chosen_parameters = st.multiselect("Parameters", parameter_options, default=parameter_options, key="explorer_parameters")
            explorer = explorer[explorer["location_name"].isin(chosen_stations) & explorer["parameter"].isin(chosen_parameters)]
            if "datetime_utc" in explorer:
                explorer = explorer.sort_values("datetime_utc", ascending=False)
    else:
        if meteo_df.empty:
            empty_message("Open-Meteo CSV is unavailable.")
            explorer = pd.DataFrame()
        else:
            meteo_columns = list(meteo_df.columns)
            chosen_columns = st.multiselect("Columns to display", meteo_columns, default=meteo_columns, key="explorer_meteo_columns")
            explorer = meteo_df[chosen_columns].copy() if chosen_columns else pd.DataFrame()
    if "explorer" in locals() and not explorer.empty:
        st.caption(f"Records shown: {len(explorer):,}")
        st.dataframe(explorer, use_container_width=True, hide_index=True)
        csv_bytes = explorer.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download filtered dataset as CSV",
            data=csv_bytes,
            file_name="ecoair_filtered_data.csv",
            mime="text/csv",
        )

# -------------------- Footer --------------------
st.divider()
st.markdown(
    """
    <div style="text-align:center;color:#64748B;padding:10px;">
    <b>EcoAir</b> · Programming for AI project · Lahore air-quality exploration<br>
    OpenAQ station measurements and Open-Meteo model-based estimates are shown separately.
    </div>
    """,
    unsafe_allow_html=True,
)
