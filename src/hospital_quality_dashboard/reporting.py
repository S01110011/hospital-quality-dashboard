"""Command line reporting utilities."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from hospital_quality_dashboard.config import DEFAULT_DATA_PATH, DEFAULT_KPI_EXPORT_PATH
from hospital_quality_dashboard.data import load_or_generate_dataset
from hospital_quality_dashboard.kpis import build_kpi_table, summarize_by_dimension


def export_kpi_summary(data_path: Path, output_path: Path) -> Path:
    df = load_or_generate_dataset(data_path)
    kpi_table = build_kpi_table(df)
    unit_summary = summarize_by_dimension(df, "unit")

    export = pd.concat(
        [
            kpi_table.assign(section="overall"),
            unit_summary.assign(section="unit").rename(columns={"unit": "label"}),
        ],
        ignore_index=True,
        sort=False,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Hospital Quality Dashboard KPI summary.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_KPI_EXPORT_PATH)
    args = parser.parse_args()

    path = export_kpi_summary(args.data, args.output)
    print(f"Saved KPI summary to {path}")


if __name__ == "__main__":
    main()

