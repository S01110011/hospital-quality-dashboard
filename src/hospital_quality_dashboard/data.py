"""Synthetic hospital quality dataset generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from hospital_quality_dashboard.config import (
    DEFAULT_DATA_PATH,
    RANDOM_STATE,
    UNITS,
)


def generate_synthetic_hospital_data(rows: int = 12000, seed: int = RANDOM_STATE) -> pd.DataFrame:
    """Generate a synthetic encounter-level hospital quality dataset."""
    rng = np.random.default_rng(seed)
    start = np.datetime64("2025-01-01")
    day_offsets = rng.integers(0, 365, rows)
    admission_dates = start + day_offsets.astype("timedelta64[D]")

    unit = rng.choice(UNITS, rows, p=[0.20, 0.24, 0.19, 0.10, 0.11, 0.08, 0.08])
    service_line_by_unit = {
        "Emergency": "Internal Medicine",
        "Medical Ward": "Internal Medicine",
        "Surgical Ward": "Surgery",
        "ICU": "Critical Care",
        "Cardiology": "Cardiology",
        "Oncology": "Oncology",
        "Maternity": "Obstetrics",
    }
    service_line = np.array([service_line_by_unit[item] for item in unit])

    age = np.clip(
        rng.normal(58, 20, rows)
        + np.isin(unit, ["ICU", "Cardiology", "Oncology"]) * 8
        - (unit == "Maternity") * 28,
        0,
        98,
    ).round().astype(int)

    severity_score = np.clip(
        rng.gamma(shape=2.2, scale=1.1, size=rows)
        + (unit == "ICU") * 2.5
        + np.isin(unit, ["Oncology", "Cardiology"]) * 0.8
        + (age > 75) * 0.9,
        0,
        10,
    )

    los = np.clip(
        rng.gamma(shape=2.1, scale=1.6, size=rows)
        + severity_score * 0.55
        + (unit == "ICU") * 2.7
        + (unit == "Maternity") * -1.2,
        0.2,
        45,
    )
    discharge_dates = admission_dates + np.ceil(los).astype(int).astype("timedelta64[D]")

    infection_probability = np.clip(0.006 + 0.004 * los + 0.010 * (unit == "ICU"), 0, 0.18)
    readmission_probability = np.clip(
        0.035 + 0.012 * severity_score + 0.018 * (unit == "Oncology") + 0.014 * (age > 75),
        0,
        0.35,
    )
    mortality_probability = np.clip(
        0.004 + 0.008 * severity_score + 0.030 * (unit == "ICU") + 0.012 * (age > 80),
        0,
        0.45,
    )

    hospital_acquired_infection = rng.binomial(1, infection_probability)
    readmitted_30d = rng.binomial(1, readmission_probability)
    mortality = rng.binomial(1, mortality_probability)

    ed_wait_minutes = np.where(
        unit == "Emergency",
        np.clip(rng.normal(42, 19, rows) + severity_score * 1.4, 5, 180),
        np.nan,
    )

    available_beds = {
        "Emergency": 38,
        "Medical Ward": 84,
        "Surgical Ward": 64,
        "ICU": 24,
        "Cardiology": 36,
        "Oncology": 30,
        "Maternity": 28,
    }

    return pd.DataFrame(
        {
            "encounter_id": [f"ENC-{i:07d}" for i in range(1, rows + 1)],
            "patient_id": [f"PAT-{x:06d}" for x in rng.integers(1, rows // 2 + 2, rows)],
            "admission_date": pd.to_datetime(admission_dates),
            "discharge_date": pd.to_datetime(discharge_dates),
            "unit": unit,
            "service_line": service_line,
            "age": age,
            "severity_score": severity_score.round(2),
            "length_of_stay_days": los.round(2),
            "available_beds": [available_beds[item] for item in unit],
            "readmitted_30d": readmitted_30d,
            "hospital_acquired_infection": hospital_acquired_infection,
            "mortality": mortality,
            "ed_wait_minutes": np.round(ed_wait_minutes, 1),
        }
    )


def save_synthetic_dataset(output: Path, rows: int, seed: int = RANDOM_STATE) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_synthetic_hospital_data(rows=rows, seed=seed).to_csv(output, index=False)
    return output


def load_or_generate_dataset(path: Path = DEFAULT_DATA_PATH, rows: int = 12000) -> pd.DataFrame:
    if not path.exists():
        save_synthetic_dataset(path, rows=rows)
    return pd.read_csv(path, parse_dates=["admission_date", "discharge_date"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic hospital quality data.")
    parser.add_argument("--output", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--rows", type=int, default=12000)
    parser.add_argument("--seed", type=int, default=RANDOM_STATE)
    args = parser.parse_args()

    path = save_synthetic_dataset(args.output, args.rows, args.seed)
    print(f"Saved synthetic hospital quality dataset to {path}")


if __name__ == "__main__":
    main()
