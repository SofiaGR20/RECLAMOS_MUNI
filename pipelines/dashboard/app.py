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

is_lifetime = st.sidebar.checkbox("Ver Lifetime", value=False)

if is_lifetime:
    data = df[df["is_lifetime"] == 1].copy()
else:
    data = df[df["is_lifetime"] == 0].copy()

if not is_lifetime:
    years = sorted(data["year"].dropna().unique())
    year = st.sidebar.selectbox("Año", options=years, format_func=lambda v: f"{v:d}")
    data = data[data["year"] == year]

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
    month = st.sidebar.selectbox(
        "Mes",
        options=months,
        format_func=lambda v: month_names.get(int(v), "Desconocido"),
    )
    data = data[data["month"] == month]

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

# KPI calculations (weighted where possible)
total_requests = data["total_requests"].sum()
closed_requests = data["closed_requests"].sum()
open_requests = data["open_requests"].sum()
sla_breach_count = data["sla_breach_count"].sum()
closed_within_sla_count = data.get("closed_within_sla_count", pd.Series(dtype=float)).sum()
high_satisfaction_count = data["high_satisfaction_count"].sum()
high_priority_count = data["high_priority_count"].sum()
total_cost_soles = data["total_cost_soles"].sum()

closure_rate = (closed_requests / total_requests) if total_requests else 0
sla_breach_rate = (sla_breach_count / total_requests) if total_requests else 0
closed_within_sla_rate = (closed_within_sla_count / closed_requests) if closed_requests else 0
high_satisfaction_rate = (high_satisfaction_count / total_requests) if total_requests else 0
high_priority_rate = (high_priority_count / total_requests) if total_requests else 0
backlog_rate = (open_requests / total_requests) if total_requests else 0

avg_resolution_hours = data["avg_resolution_hours"].mean()
median_resolution_hours = data["median_resolution_hours"].mean()
p90_resolution_hours = data["p90_resolution_hours"].mean()
avg_satisfaction = data["avg_satisfaction"].mean()
avg_cost_soles = data["avg_cost_soles"].mean()

# KPI cards (two rows)
kpi_row1 = st.columns(5)
kpi_row1[0].metric("Total solicitudes", f"{total_requests:.0f}")
kpi_row1[1].metric("Tasa de cierre", f"{closure_rate:.2%}")
kpi_row1[2].metric("Incumplimiento SLA", f"{sla_breach_rate:.2%}")
kpi_row1[3].metric("Cerradas dentro de SLA", f"{closed_within_sla_rate:.2%}")
kpi_row1[4].metric("Backlog rate", f"{backlog_rate:.2%}")

kpi_row2 = st.columns(5)
kpi_row2[0].metric("Tiempo medio (h)", f"{avg_resolution_hours:.2f}")
kpi_row2[1].metric("Mediana (h)", f"{median_resolution_hours:.2f}")
kpi_row2[2].metric("P90 (h)", f"{p90_resolution_hours:.2f}")
kpi_row2[3].metric("Satisfacción promedio", f"{avg_satisfaction:.2f}")
kpi_row2[4].metric("Alta satisfacción", f"{high_satisfaction_rate:.2%}")

kpi_row3 = st.columns(4)
kpi_row3[0].metric("Alta prioridad", f"{high_priority_rate:.2%}")
kpi_row3[1].metric("Costo total (S/.)", f"{total_cost_soles:.2f}")
kpi_row3[2].metric("Costo promedio (S/.)", f"{avg_cost_soles:.2f}")
kpi_row3[3].metric("Casos abiertos", f"{open_requests:.0f}")

# Charts
st.subheader("Distribución por categoría")
cat = data.groupby("category").agg(total=("total_requests", "sum"), sla=("sla_breach_rate", "mean")).reset_index()
st.bar_chart(cat.set_index("category")["total"])

st.subheader("Distribución por canal")
canal = data.groupby("channel").agg(total=("total_requests", "sum"), sla=("sla_breach_rate", "mean")).reset_index()
st.bar_chart(canal.set_index("channel")["total"])

st.subheader("Tabla resumen")
st.dataframe(data.head(200))
