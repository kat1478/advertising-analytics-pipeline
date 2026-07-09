# Advertising Analytics Data Pipeline

This is a professional-grade data engineering portfolio project that demonstrates a robust, reproducible pipeline for advertising analytics. 

## Business Objective
The pipeline mimics a cloud data warehouse workflow using local tools. It takes synthetic ad data, loads it into raw tables, applies SQL transformations to create analytical marts, and generates a business-ready markdown report.

## Architecture
```text
synthetic ad data → raw tables → staging SQL → analytical marts → report → insights → tests → CI
```

## Core Stack
- **Python 3.11+** for data generation, orchestration, and testing
- **DuckDB** for the local data warehouse
- **SQL** for staging and analytical models
- **pandas** for data manipulation
- **pytest** for data quality and pipeline testing
- **GitHub Actions** for CI
