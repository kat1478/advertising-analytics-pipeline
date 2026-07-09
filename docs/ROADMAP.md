# Roadmap

## v0.1.0 — Repository foundation

- project scaffold
- clean README
- git workflow docs
- branch protection setup
- initial CI placeholder

## v0.2.0 — Synthetic data generation

- campaigns, products, impressions, clicks, costs, conversions
- deterministic random seed
- realistic advertising relationships
- intentional data quality edge cases

## v0.3.0 — DuckDB raw loading

- load CSV or Parquet into DuckDB
- create raw tables
- pipeline entrypoint

## v0.4.0 — SQL staging layer

- typed and cleaned staging tables
- deduplication
- basic data quality checks

## v0.5.0 — Analytical marts

- dimensions
- fact table
- daily campaign performance
- category performance

## v0.6.0 — Testing and data quality

- pytest data quality tests
- metric tests
- pipeline smoke test

## v0.7.0 — Report generation

- Markdown campaign report
- top and bottom campaign tables
- anomaly-style insights

## v0.8.0 — Analytics assistant

- rule-based business insight generator
- optional local LLM integration later

## v1.0.0 — Portfolio release

- polished README
- architecture diagram
- example report
- full CI passing
- tagged stable release
