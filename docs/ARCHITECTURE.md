# Architecture

This document describes the architectural layout and design choices implemented in the Advertising Analytics Data Pipeline.

## Layer Responsibilities

The project follows a standard modern data stack layer pattern:
1. **Raw**: Unstructured or semi-structured data directly ingested from the synthetic generator into DuckDB tables. It represents the pristine state of data before any business logic is applied.
2. **Staging**: Cleaned, typed, and deduplicated tables. Staging serves as the foundation for complex joins and acts as a firewall against upstream data quality issues.
3. **Marts**: Highly modeled business tables (Dimensions and Facts). These tables are aggregated, metric-rich, and ready for end-user reporting.

## Pipeline Execution Order

The pipeline relies on a strict sequential execution order enforced by Python orchestration:
1. Synthetic Data Generation
2. Raw Ingestion into DuckDB
3. Raw Data Quality Validation
4. Staging SQL Transformations
5. Analytical Marts SQL Transformations
6. Metric Quality Assurance Tests
7. Markdown Reporting & Insight Generation

## Fact Table Grain & Cost Allocation

The primary fact table (`fact_ad_events`) resolves data to an individual event grain (impressions, clicks, conversions) tied to a specific `event_date`.
Because advertising costs are commonly supplied at a daily aggregate campaign level, we use a proportional allocation approach. Daily costs are proportionally distributed across the campaign's impressions to ensure revenue and ROAS can be measured effectively at the lowest grain.

## Attribution Choice

The pipeline uses an **impression-based attribution cohort model**. Rather than logging clicks and conversions strictly on the calendar day they occurred, they are joined back to the originating impression's timestamp. This decision guarantees that funnel metrics (`impressions >= clicks >= conversions`) remain mathematically consistent on any given reporting day.

## Reporting Outputs

The finalized metrics are exported into localized Markdown artifacts (`reports/campaign_report.md` and `reports/analytics_insights.md`). This eliminates the need for external BI tools during the portfolio review process and ensures outputs are natively reviewable directly within the GitHub interface.

## Why DuckDB?

DuckDB was selected as the local analytical warehouse because:
- It eliminates the overhead of managing Postgres, Snowflake, or BigQuery instances.
- It operates incredibly fast on local CSV files and in-memory data processing.
- It provides a robust, PostgreSQL-compatible SQL dialect capable of heavy analytical window functions.
- It naturally fits a reproducible "clone-and-run" Python portfolio project.
