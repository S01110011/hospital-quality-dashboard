from hospital_quality_dashboard.data import generate_synthetic_hospital_data
from hospital_quality_dashboard.kpis import build_kpi_table, calculate_kpis, filter_encounters, summarize_by_dimension


def test_calculate_kpis_returns_expected_metrics():
    df = generate_synthetic_hospital_data(rows=500, seed=321)
    metrics = calculate_kpis(df)

    assert metrics["encounters"] == 500
    assert metrics["discharges"] == 500
    assert metrics["avg_length_of_stay"] > 0
    assert 0 <= metrics["readmission_rate"] <= 1
    assert 0 <= metrics["mortality_rate"] <= 1


def test_build_kpi_table_includes_target_statuses():
    df = generate_synthetic_hospital_data(rows=500, seed=456)
    table = build_kpi_table(df)

    assert {"label", "metric", "value", "unit", "status"}.issubset(table.columns)
    assert table["status"].notna().all()
    assert "Bed Occupancy" in set(table["label"])


def test_filter_and_dimension_summary():
    df = generate_synthetic_hospital_data(rows=500, seed=789)
    filtered = filter_encounters(df, units=["ICU"])
    summary = summarize_by_dimension(filtered, "unit")

    assert set(filtered["unit"]) == {"ICU"}
    assert len(summary) == 1
    assert summary.iloc[0]["unit"] == "ICU"

