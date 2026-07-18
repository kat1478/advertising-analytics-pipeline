# Architecture

This document describes the architectural layout and design choices implemented in the Advertising Analytics Data Pipeline.

## Layer Responsibilities

The project follows a standard analytical layer pattern:

1. **Raw**: Data directly ingested from the synthetic generator into DuckDB tables. Represents the pristine, unmodified state before any business logic is applied.
2. **Staging**: Cleaned, typed, and deduplicated tables. Staging acts as a firewall against upstream data quality issues and provides a stable foundation for mart joins.
3. **Marts**: Business-modeled tables (Dimensions, Fact, and derived aggregates). These tables are metric-rich and designed for reporting consumption.

## Pipeline Execution Order

A unified sequential runner (`src/run_pipeline.py`) executes every step in order within a single Python process:

```bash
python -m src.run_pipeline
```

This is a **sequential, in-process Python orchestrator** — not a distributed workflow scheduler. It does not use Prefect, Airflow, or any external scheduler. Each step is called as a Python function and any failure is propagated immediately.

Steps executed in order:
1. Synthetic data generation
2. DuckDB raw ingestion
3. Raw data validation
4. SQL staging + mart transformations
5. Markdown performance report
6. Analytics insights
7. Output verification (tables + reports)

Individual steps can also be run manually:

```bash
python -m src.generate_data
python -m src.load_raw
python -m src.validate_data
python -m src.run_sql
python -m src.generate_report
python -m src.analytics_assistant
```

## Raw / Staging / Marts Separation

| Layer | Tables | Responsibility |
|---|---|---|
| Raw | `raw_campaigns`, `raw_products`, `raw_impressions`, `raw_clicks`, `raw_costs`, `raw_conversions` | Faithful copy of source data |
| Staging | `stg_campaigns`, `stg_products`, `stg_impressions`, `stg_clicks`, `stg_costs`, `stg_conversions` | Type casting, deduplication, null handling |
| Marts | `dim_campaigns`, `dim_products`, `fact_campaign_product_daily`, `daily_campaign_performance`, `category_performance` | Business metrics, joins, aggregations |

## Fact Table Grain

The primary fact table is `fact_campaign_product_daily`.

**Grain: `event_date × campaign_id × product_id`**

Each row represents the aggregated advertising activity (impressions, clicks, conversions, allocated cost, revenue) for one campaign advertising one product on one calendar day.  This is **not** an individual-event table — rows are aggregates.

Derived aggregation marts:
- `daily_campaign_performance` — aggregates `fact_campaign_product_daily` across all products per campaign-day
- `category_performance` — aggregates across all campaigns per product category (no time dimension)

## Cost Allocation Approach

Advertising costs arrive at the campaign × daily grain (`raw_costs`). The fact table operates at the lower campaign × product × daily grain. Daily campaign costs are distributed proportionally across products based on their share of that campaign's daily impressions:

```
Product Cost = Campaign Daily Cost × (Product Impressions / Total Campaign Impressions)
```

Automated tests verify cost reconciliation: the sum of allocated costs per campaign-day must match the source cost (within a 0.01 PLN tolerance).

## Attribution Choice

The pipeline uses **impression-based attribution cohorts**:
- Clicks and conversions are joined back to the originating impression.
- All downstream events inherit the impression's `event_date`.
- This guarantees daily funnel consistency: `impressions >= clicks >= conversions` always holds per cohort day.

This is a deliberate analytical design choice for this project, not the only valid industry model.

## Reporting Outputs

Final metrics are exported to Markdown artifacts:
- `reports/campaign_report.md` — quantitative performance report
- `reports/analytics_insights.md` — classified campaign recommendations

These files contain only deterministic synthetic data and are safe to commit. Runtime timestamps are not embedded; deterministic metadata (dataset seed, reporting period, currency) is used instead.

## Why DuckDB?

DuckDB was selected as the local analytical storage because:
- It operates as an embedded, file-based database with zero infrastructure setup.
- It executes analytical SQL queries very efficiently on local data.
- Its SQL dialect is inspired by PostgreSQL but is not fully compatible — some PostgreSQL extensions are not available.
- It naturally supports a reproducible "clone-and-run" portfolio project without requiring cloud credentials.
