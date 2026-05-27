"""Hospital quality KPI calculation layer."""

from __future__ import annotations

import pandas as pd

from hospital_quality_dashboard.config import QUALITY_TARGETS


def filter_encounters(
    df: pd.DataFrame,
    start_date: str | pd.Timestamp | None = None,
    end_date: str | pd.Timestamp | None = None,
    units: list[str] | None = None,
    service_lines: list[str] | None = None,
) -> pd.DataFrame:
    """Filter encounters by date, unit and service line."""
    filtered = df.copy()
    if start_date is not None:
        filtered = filtered[filtered["admission_date"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        filtered = filtered[filtered["admission_date"] <= pd.Timestamp(end_date)]
    if units:
        filtered = filtered[filtered["unit"].isin(units)]
    if service_lines:
        filtered = filtered[filtered["service_line"].isin(service_lines)]
    return filtered


def calculate_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Calculate executive hospital quality KPIs from encounter-level data."""
    if df.empty:
        return {
            "encounters": 0,
            "discharges": 0,
            "occupancy_rate": 0.0,
            "avg_length_of_stay": 0.0,
            "readmission_rate": 0.0,
            "infection_rate_per_100": 0.0,
            "mortality_rate": 0.0,
            "median_ed_wait_minutes": 0.0,
        }

    period_days = max((df["admission_date"].max() - df["admission_date"].min()).days + 1, 1)
    bed_days_used = float(df["length_of_stay_days"].sum())
    average_beds = float(df.groupby("unit")["available_beds"].max().sum())
    available_bed_days = max(average_beds * period_days, 1.0)
    ed_wait = df["ed_wait_minutes"].dropna()

    return {
        "encounters": int(len(df)),
        "discharges": int(df["discharge_date"].notna().sum()),
        "occupancy_rate": bed_days_used / available_bed_days,
        "avg_length_of_stay": float(df["length_of_stay_days"].mean()),
        "readmission_rate": float(df["readmitted_30d"].mean()),
        "infection_rate_per_100": float(df["hospital_acquired_infection"].mean() * 100),
        "mortality_rate": float(df["mortality"].mean()),
        "median_ed_wait_minutes": float(ed_wait.median()) if not ed_wait.empty else 0.0,
    }


def target_status(metric: str, value: float) -> str:
    """Compare one metric against its quality target."""
    target = QUALITY_TARGETS[metric]
    margin = target["warning_margin"]

    if target["operator"] == "max":
        if value <= target["value"]:
            return "on_target"
        if value <= target["value"] + margin:
            return "watch"
        return "off_target"

    lower = target["lower"]
    upper = target["upper"]
    if lower <= value <= upper:
        return "on_target"
    if lower - margin <= value <= upper + margin:
        return "watch"
    return "off_target"


def build_kpi_table(df: pd.DataFrame) -> pd.DataFrame:
    """Return KPI table with values, display labels and target status."""
    kpis = calculate_kpis(df)
    rows = [
        ("Encounters", "encounters", kpis["encounters"], "count", "volume"),
        ("Discharges", "discharges", kpis["discharges"], "count", "volume"),
        ("Bed Occupancy", "occupancy_rate", kpis["occupancy_rate"], "percent", "quality"),
        ("Average LOS", "avg_length_of_stay", kpis["avg_length_of_stay"], "days", "quality"),
        ("30-Day Readmission", "readmission_rate", kpis["readmission_rate"], "percent", "quality"),
        (
            "HAI Rate",
            "infection_rate_per_100",
            kpis["infection_rate_per_100"],
            "per_100",
            "quality",
        ),
        ("Mortality", "mortality_rate", kpis["mortality_rate"], "percent", "quality"),
        (
            "Median ED Wait",
            "median_ed_wait_minutes",
            kpis["median_ed_wait_minutes"],
            "minutes",
            "quality",
        ),
    ]
    table = pd.DataFrame(rows, columns=["label", "metric", "value", "unit", "category"])
    table["status"] = table.apply(
        lambda row: target_status(row["metric"], row["value"])
        if row["metric"] in QUALITY_TARGETS
        else "not_applicable",
        axis=1,
    )
    return table


def summarize_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Calculate comparable quality KPIs by unit or service line."""
    summaries = []
    for value, group in df.groupby(dimension):
        metrics = calculate_kpis(group)
        metrics[dimension] = value
        summaries.append(metrics)
    if not summaries:
        return pd.DataFrame()
    return pd.DataFrame(summaries).sort_values("encounters", ascending=False)

