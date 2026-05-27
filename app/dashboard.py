"""Streamlit dashboard for hospital quality and patient-safety indicators."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from hospital_quality_dashboard.data import load_or_generate_dataset
from hospital_quality_dashboard.kpis import build_kpi_table, filter_encounters, summarize_by_dimension


st.set_page_config(page_title="Hospital Quality Dashboard", page_icon="+", layout="wide")


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    return load_or_generate_dataset()


def format_metric(value: float, unit: str) -> str:
    if unit == "percent":
        return f"{value:.1%}"
    if unit == "per_100":
        return f"{value:.2f}"
    if unit == "days":
        return f"{value:.1f}"
    if unit == "minutes":
        return f"{value:.0f}"
    return f"{int(value):,}"


def status_icon(status: str) -> str:
    return {"on_target": "OK", "watch": "WATCH", "off_target": "ACTION"}.get(status, "NA")


df = load_data()

st.title("Hospital Quality Dashboard")
st.caption("Quality, safety and operational indicators across hospital units.")

with st.sidebar:
    st.header("Filters")
    min_date = df["admission_date"].min().date()
    max_date = df["admission_date"].max().date()
    date_range = st.date_input("Admission period", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    selected_units = st.multiselect("Units", sorted(df["unit"].unique()), default=sorted(df["unit"].unique()))
    selected_service_lines = st.multiselect(
        "Service lines",
        sorted(df["service_line"].unique()),
        default=sorted(df["service_line"].unique()),
    )

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = filter_encounters(
    df,
    start_date=pd.Timestamp(start_date),
    end_date=pd.Timestamp(end_date),
    units=selected_units,
    service_lines=selected_service_lines,
)
kpi_table = build_kpi_table(filtered)

quality_kpis = kpi_table[kpi_table["category"] == "quality"]
volume_kpis = kpi_table[kpi_table["category"] == "volume"]

volume_cols = st.columns(len(volume_kpis))
for col, (_, row) in zip(volume_cols, volume_kpis.iterrows(), strict=False):
    col.metric(row["label"], format_metric(row["value"], row["unit"]))

quality_cols = st.columns(3)
for idx, (_, row) in enumerate(quality_kpis.iterrows()):
    with quality_cols[idx % 3]:
        st.metric(row["label"], format_metric(row["value"], row["unit"]), status_icon(row["status"]))

st.divider()

left, right = st.columns([1.15, 1])

unit_summary = summarize_by_dimension(filtered, "unit")
service_summary = summarize_by_dimension(filtered, "service_line")

with left:
    st.subheader("Unit Comparison")
    selected_metric = st.selectbox(
        "Metric",
        [
            "occupancy_rate",
            "avg_length_of_stay",
            "readmission_rate",
            "infection_rate_per_100",
            "mortality_rate",
            "median_ed_wait_minutes",
        ],
        format_func=lambda item: item.replace("_", " ").title(),
    )
    if not unit_summary.empty:
        fig = px.bar(
            unit_summary,
            x="unit",
            y=selected_metric,
            color="unit",
            text_auto=".2f",
            labels={"unit": "Unit", selected_metric: selected_metric.replace("_", " ").title()},
        )
        fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Service Line Volume")
    if not service_summary.empty:
        fig = px.pie(service_summary, names="service_line", values="encounters", hole=0.45)
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

st.subheader("KPI Detail")
display_table = kpi_table.copy()
display_table["value"] = display_table.apply(lambda row: format_metric(row["value"], row["unit"]), axis=1)
st.dataframe(display_table[["label", "value", "unit", "status"]], use_container_width=True, hide_index=True)

st.download_button(
    "Download KPI table",
    data=kpi_table.to_csv(index=False),
    file_name="hospital_quality_kpis.csv",
    mime="text/csv",
)

