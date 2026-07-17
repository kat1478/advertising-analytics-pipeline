# Advertising Analytics Data Pipeline

This is a professional-grade data engineering portfolio project that demonstrates a robust, reproducible pipeline for advertising analytics. 
The project addresses the business problem of analyzing advertising campaign performance, tracking spending, and evaluating return on ad spend (ROAS).
It uses a synthetic advertising dataset, mimicking a cloud data warehouse workflow entirely with local tools.

## Project Overview

The project implements an end-to-end analytical workflow:

synthetic data → raw ingestion → data quality validation → SQL staging → analytical marts → metric quality tests → Markdown report → rule-based business insights

## Business Questions

This pipeline is designed to answer core business questions:
- Which campaigns generate the highest ROAS?
- Which campaigns attract clicks but fail to convert?
- Which product categories generate the most revenue?
- Which campaigns have high acquisition costs?
- Can downstream reports trust the underlying data?

## Architecture

```mermaid
flowchart LR
    A[Synthetic CSV Data] --> B[DuckDB Raw Tables]
    B --> C[Raw Data Validation]
    C --> D[SQL Staging Tables]
    D --> E[Analytical Marts]
    E --> F[Performance Report]
    E --> G[Analytics Insights]
```

- **Python**: Responsible for data generation, extraction, pipeline orchestration, reporting, and insight generation.
- **SQL**: Responsible for staging and analytical data modeling.
- **DuckDB**: Serves as the local analytical storage.
- **pytest**: Enforces rigorous validation on raw data and final metric outputs.

## Data Model

The pipeline transforms data through several layers:

**Raw Layer:**
- `raw_campaigns`
- `raw_products`
- `raw_impressions`
- `raw_clicks`
- `raw_costs`
- `raw_conversions`

**Staging Layer:**
- `stg_campaigns`
- `stg_products`
- `stg_impressions`
- `stg_clicks`
- `stg_costs`
- `stg_conversions`

**Marts Layer:**
- `dim_campaigns`
- `dim_products`
- `fact_ad_events`
- `daily_campaign_performance`
- `category_performance`

```mermaid
erDiagram
    dim_campaigns ||--o{ fact_ad_events : "1 to N"
    dim_products ||--o{ fact_ad_events : "1 to N"
    fact_ad_events }o--|| daily_campaign_performance : "Aggregated by"
    fact_ad_events }o--|| category_performance : "Aggregated by"
```

## Advertising Metrics

The pipeline calculates key performance indicators natively:
- **CTR (Click-Through Rate)**
- **CPC (Cost Per Click)**
- **Conversion Rate**
- **ROAS (Return on Ad Spend)**
- **Cost per Conversion**

For detailed definitions, formulas, and metric assumptions, see [docs/METRICS.md](docs/METRICS.md).

## Data Quality

The project implements an extensive automated `pytest` suite enforcing data quality constraints:
- required tables exist
- null primary keys are prevented
- duplicate identifiers are rejected
- foreign-key relationships are maintained
- financial metrics are strictly non-negative
- funnel consistency is logically bounded
- metric ranges (e.g. CTR between 0 and 1)
- allocated cost reconciliation against source data
- safe division to prevent zero-division errors

## Attribution Model

The pipeline relies on **impression-based attribution**. 
- Clicks and conversions are connected back to the originating impression.
- Downstream events are assigned to the impression cohort date.
- This preserves daily funnel consistency (impressions >= clicks >= conversions).

Note: This is not the only valid industry attribution model, but it is a deliberate analytical choice for this project to maintain strict funnel cohort alignment.

## Project Structure

```text
.
├── docs/
│   ├── ARCHITECTURE.md
│   ├── METRICS.md
│   ├── PROJECT_CHARTER.md
│   ├── REPORTING.md
│   └── ROADMAP.md
├── reports/
│   ├── analytics_insights.md
│   └── campaign_report.md
├── sql/
│   ├── marts/
│   └── staging/
├── src/
│   ├── analytics_assistant.py
│   ├── config.py
│   ├── generate_data.py
│   ├── generate_report.py
│   ├── load_raw.py
│   ├── paths.py
│   ├── run_pipeline.py
│   ├── run_sql.py
│   └── validate_data.py
├── tests/
│   ├── test_analytics_assistant.py
│   ├── test_generate_report.py
│   ├── test_marts_sql.py
│   ├── test_metrics_quality.py
│   └── test_staging_sql.py
├── environment.yml
└── pyproject.toml
```

## Getting Started

This project uses `mamba` to ensure consistent dependency management.

1. **Create the environment:**
   ```bash
   mamba env create -f environment.yml
   ```
2. **Activate the environment:**
   ```bash
   mamba activate ads-analytics-pipeline
   ```

Then execute the pipeline steps in sequence:
```bash
python -m src.generate_data
python -m src.load_raw
python -m src.validate_data
python -m src.run_sql
python -m src.generate_report
python -m src.analytics_assistant
```

## Testing

Run the full testing suite via pytest:
```bash
python -m pytest -q
```

The tests cover:
- generation
- ingestion
- validation
- staging
- marts
- metric quality
- reporting
- analytics insights

## Example Outputs

The pipeline automatically generates formatted markdown outputs showcasing the final metrics:
- [Performance Report](reports/campaign_report.md)
- [Analytics Insights](reports/analytics_insights.md)

## Key Engineering Decisions

- **DuckDB** as a fast, file-based local analytical warehouse.
- **SQL-first** transformations to mimic dbt-like workflows.
- **Python** for orchestration, data manipulation, and testing.
- **Deterministic synthetic data** ensuring reproducibility without privacy risks.
- **Layered architecture** cleanly separating raw, staging, and marts layers.
- **Rule-based analytics assistant** to translate mathematical metrics into actions without requiring external LLM API keys.
- **Automated quality tests** protecting analytical outputs from regression.

## What This Project Demonstrates

This repository is built to showcase standard competencies:
- Data pipeline design
- Analytical data modeling
- SQL transformations
- Data quality engineering
- Metric definition and testing
- Reproducibility
- Business-oriented reporting
- Git and pull-request workflow

## Limitations

- Synthetic rather than real production data
- Local DuckDB rather than a cloud warehouse
- Batch rather than streaming processing
- Rule-based assistant rather than an LLM
- Simplified attribution model
- No production deployment yet

## Roadmap

Future planned improvements:
- End-to-end pipeline orchestrator
- GitHub Actions hardening
- Prefect orchestration
- Streamlit dashboard
- Optional Ollama integration
- BigQuery-compatible SQL
- Cloud deployment
