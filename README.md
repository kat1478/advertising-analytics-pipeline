# Advertising Analytics Data Pipeline

This is a professional-grade data engineering portfolio project that demonstrates a robust, reproducible pipeline for advertising analytics. 

## Business Objective
The pipeline mimics a cloud data warehouse workflow using local tools. It takes synthetic ad data, loads it into raw tables, and applies SQL transformations to create analytical marts.

## Architecture
```text
synthetic ad data → raw tables → staging SQL → analytical marts → metrics quality tests → CI
```

## Key Components
- **Data Generation:** Deterministic synthetic data generator.
- **Local Data Warehouse:** DuckDB for fast OLAP queries.
- **Data Modeling:** Layered SQL transformations (raw, staging, and analytical marts).
- **Data Quality & Testing:** Comprehensive `pytest` suite for raw data validation and metric correctness (see [METRICS.md](docs/METRICS.md)).

## Core Stack
- **Python 3.11+** for data generation, orchestration, and testing
- **DuckDB** for the local data warehouse
- **SQL** for staging and analytical models
- **pandas** for data manipulation
- **pytest** for data quality and pipeline testing
- **GitHub Actions** for CI

## Setup Instructions

This project uses `mamba` (or `conda`) for environment management to ensure consistent dependencies.

1. **Create the environment:**
   ```bash
   mamba env create -f environment.yml
   ```
2. **Activate the environment:**
   ```bash
   mamba activate ads-analytics-pipeline
   ```

**Fallback (pip):**
If you do not use `mamba` or `conda`, you can install the dependencies via `pip`:
```bash
python -m pip install -r requirements.txt
```

## Running the Pipeline

To execute the data pipeline and generate the business report, run the following commands in order:

```bash
python -m src.generate_data
python -m src.load_raw
python -m src.validate_data
python -m src.run_sql
python -m src.generate_report
```

A sample Markdown report will be generated from the analytical marts and saved to `reports/campaign_report.md`.
