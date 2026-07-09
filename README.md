# Advertising Analytics Data Pipeline

A portfolio-grade data engineering project that processes synthetic advertising data, validates data quality, builds analytical marts, and generates business-readable campaign insights.

The project is designed locally to mirror cloud warehouse workflows such as BigQuery-style analytical transformations, while staying lightweight and reproducible with Python, SQL, and DuckDB.

## Business context

The pipeline models a simplified advertising analytics workflow:

1. Campaigns generate ad impressions.
2. Some impressions lead to clicks.
3. Some clicks lead to conversions and revenue.
4. Daily campaign and category performance tables are built for reporting.
5. Data quality checks protect downstream metrics from bad input data.

## Target architecture

```text
raw CSV/Parquet
    ↓
DuckDB raw tables
    ↓
SQL staging layer
    ↓
SQL marts layer
    ↓
Markdown report / analytics insights
    ↓
pytest + GitHub Actions validation
```

## Planned data model

### Raw layer

- `raw_campaigns`
- `raw_products`
- `raw_impressions`
- `raw_clicks`
- `raw_costs`
- `raw_conversions`

### Staging layer

- `stg_campaigns`
- `stg_products`
- `stg_impressions`
- `stg_clicks`
- `stg_costs`
- `stg_conversions`

### Marts layer

- `dim_campaigns`
- `dim_products`
- `fact_ad_events`
- `daily_campaign_performance`
- `category_performance`

## Core metrics

- CTR = clicks / impressions
- CPC = cost / clicks
- Conversion rate = conversions / clicks
- ROAS = revenue / cost
- Cost per conversion = cost / conversions

All ratio metrics are calculated with safe division to avoid division-by-zero errors.

## Quality checks

Planned checks include:

- non-null primary and foreign keys
- no negative costs or revenue
- no duplicate event identifiers
- conversions linked to existing clicks
- clicks linked to existing impressions
- metric ranges such as CTR between 0 and 1
- daily performance uniqueness by `event_date` and `campaign_id`

## Repository workflow

This repository uses a protected branch workflow:

- `master` contains stable portfolio releases.
- `develop` contains integrated work ready for release review.
- feature branches are created from `develop` and merged back through pull requests.

See [`docs/GIT_WORKFLOW.md`](docs/GIT_WORKFLOW.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md).
