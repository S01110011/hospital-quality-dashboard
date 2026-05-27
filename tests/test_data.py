from hospital_quality_dashboard.config import SERVICE_LINES, UNITS
from hospital_quality_dashboard.data import generate_synthetic_hospital_data


def test_generate_synthetic_hospital_data_has_expected_columns():
    df = generate_synthetic_hospital_data(rows=300, seed=123)

    assert len(df) == 300
    assert set(df["unit"]).issubset(set(UNITS))
    assert set(df["service_line"]).issubset(set(SERVICE_LINES))
    assert df["length_of_stay_days"].gt(0).all()
    assert df["mortality"].isin([0, 1]).all()

