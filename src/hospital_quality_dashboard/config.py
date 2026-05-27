"""Project configuration and quality targets."""

from pathlib import Path

RANDOM_STATE = 42
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "hospital_quality_synthetic.csv"
DEFAULT_KPI_EXPORT_PATH = PROJECT_ROOT / "data" / "kpi_summary.csv"

QUALITY_TARGETS = {
    "occupancy_rate": {"operator": "between", "lower": 0.75, "upper": 0.92, "warning_margin": 0.04},
    "avg_length_of_stay": {"operator": "max", "value": 5.8, "warning_margin": 0.5},
    "readmission_rate": {"operator": "max", "value": 0.095, "warning_margin": 0.015},
    "infection_rate_per_100": {"operator": "max", "value": 3.0, "warning_margin": 0.5},
    "mortality_rate": {"operator": "max", "value": 0.035, "warning_margin": 0.006},
    "median_ed_wait_minutes": {"operator": "max", "value": 45.0, "warning_margin": 10.0},
}

UNITS = [
    "Emergency",
    "Medical Ward",
    "Surgical Ward",
    "ICU",
    "Cardiology",
    "Oncology",
    "Maternity",
]

SERVICE_LINES = [
    "Internal Medicine",
    "Surgery",
    "Critical Care",
    "Cardiology",
    "Oncology",
    "Obstetrics",
]

