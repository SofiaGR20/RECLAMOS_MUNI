import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Dashboard Servicio al Usuario", layout="wide")

BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data" / "gold" / "dashboard_reclamos.parquet"

@st.cache_data
def load_data():
    return pd.read_parquet(DATA)

df = load_data()
df["year"] = df["year"].fillna(0).astype(int)
df["month"] = df["month"].fillna(0).astype(int)

# Filters
st.sidebar.header("Filtros")

is_lifetime = st.sidebar.checkbox("Ver Lifetime", value=True)

if is_lifetime:
    data = df[df["is_lifetime"] == 1].copy()
else:
    data = df[df["is_lifetime"] == 0].copy()

if not is_lifetime:
    years = sorted(data["year"].dropna().unique())
    years_sel = st.sidebar.multiselect(
        "Año",
        options=years,
        default=years,
        format_func=lambda v: f"{v:d}",
    )
    if years_sel:
        data = data[data["year"].isin(years_sel)]

    months = sorted(data["month"].dropna().unique())
    month_names = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }
    months_sel = st.sidebar.multiselect(
        "Mes",
        options=months,
        default=months,
        format_func=lambda v: month_names.get(int(v), "Desconocido"),
    )
    if months_sel:
        data = data[data["month"].isin(months_sel)]

category = st.sidebar.multiselect("Categoría", sorted(data["category"].unique()))
if category:
    data = data[data["category"].isin(category)]

channel = st.sidebar.multiselect("Canal", sorted(data["channel"].unique()))
if channel:
    data = data[data["channel"].isin(channel)]

status = st.sidebar.multiselect("Estado", sorted(data["status"].unique()))
if status:
    data = data[data["status"].isin(status)]

st.title("Dashboard de Servicio al Usuario")

# Line charts: yearly then monthly requests
monthly = df[df["is_lifetime"] == 0].copy()
if not is_lifetime:
    if years_sel:
        monthly = monthly[monthly["year"].isin(years_sel)]
    if months_sel:
        monthly = monthly[monthly["month"].isin(months_sel)]
if category:
    monthly = monthly[monthly["category"].isin(category)]
if channel:
    monthly = monthly[monthly["channel"].isin(channel)]
if status:
    monthly = monthly[monthly["status"].isin(status)]

if not monthly.empty:
    yearly = (
        monthly.groupby("year", dropna=True)
        .agg(total=("total_requests", "sum"))
        .reset_index()
        .sort_values("year")
    )
    st.subheader("Tendencia anual de reclamos")
    st.line_chart(yearly.set_index("year")["total"])

    ts = (
        monthly.groupby("month_start", dropna=True)
        .agg(total=("total_requests", "sum"))
        .reset_index()
        .sort_values("month_start")
    )
    st.subheader("Tendencia mensual de reclamos")
    st.line_chart(ts.set_index("month_start")["total"])

# KPI cards
kpi_cols = st.columns(5)

def metric(col, label, fmt="{:.2f}"):
    val = data[col].sum() if col in ["total_requests", "closed_requests", "open_requests", "sla_breach_count", "high_priority_count"] else data[col].mean()
    kpi_cols.pop(0).metric(label, fmt.format(val) if isinstance(val, (int, float)) else val)

metric("total_requests", "Total solicitudes", "{:.0f}")
metric("closure_rate", "Tasa de cierre")
metric("sla_breach_rate", "Incumplimiento SLA")
metric("avg_resolution_hours", "Tiempo medio (h)")
metric("avg_satisfaction", "Satisfacción promedio")

# Charts
st.subheader("Distribución por categoría")
cat = data.groupby("category").agg(total=("total_requests", "sum"), sla=("sla_breach_rate", "mean")).reset_index()
st.bar_chart(cat.set_index("category")["total"])

st.subheader("Distribución por canal")
canal = data.groupby("channel").agg(total=("total_requests", "sum"), sla=("sla_breach_rate", "mean")).reset_index()
st.bar_chart(canal.set_index("channel")["total"])

st.subheader("Tabla resumen")
display_df = data.copy()
if is_lifetime:
    display_df["year"] = "Lifetime"
    display_df["month"] = ""
st.dataframe(display_df.head(200))
