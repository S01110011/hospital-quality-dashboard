# Hospital Quality Dashboard

Hospital Quality Dashboard is a professional Python project for monitoring hospital quality, safety and operational performance indicators.

The project uses synthetic hospital data by default, making it safe for a public GitHub portfolio while still reflecting realistic healthcare analytics workflows.

## Clinical And Hospital Challenge

Hospital leadership teams need reliable visibility into quality indicators across units and service lines. This dashboard helps monitor:

- Bed occupancy
- Average length of stay
- 30-day readmission rate
- Hospital-acquired infection rate
- In-hospital mortality rate
- Emergency department waiting time
- Discharge volume
- Unit-level target compliance

## Features

- Synthetic hospital encounter generation
- Reproducible KPI calculation layer
- Streamlit dashboard with executive filters
- Unit and service-line comparison
- Quality target status flags
- CSV export for BI handoff
- Pytest coverage for data and KPI logic
- GitHub Actions CI

## Project Structure

```text
hospital-quality-dashboard/
├── app/
│   └── dashboard.py
├── data/
│   └── README.md
├── docs/
│   └── metric_definitions.md
├── src/
│   └── hospital_quality_dashboard/
│       ├── __init__.py
│       ├── config.py
│       ├── data.py
│       ├── kpis.py
│       └── reporting.py
├── tests/
│   ├── test_data.py
│   └── test_kpis.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .gitignore
├── pyproject.toml
└── README.md
```

## Quickstart

From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Generate synthetic data:

```powershell
python -m hospital_quality_dashboard.data --output data/hospital_quality_synthetic.csv --rows 12000
```

Export KPI tables:

```powershell
python -m hospital_quality_dashboard.reporting --data data/hospital_quality_synthetic.csv --output data/kpi_summary.csv
```

Run the dashboard:

```powershell
python -m streamlit run app/dashboard.py
```

Run tests and lint:

```powershell
python -m pytest
python -m ruff check .
```

## Portfolio Notes

This project demonstrates practical analytics skills used in healthtech and hospital data teams:

- Healthcare KPI definition
- Reproducible data transformation
- Executive dashboard design
- Quality and patient-safety reporting
- Python packaging and CI

This is not a medical device or official hospital quality reporting system.

