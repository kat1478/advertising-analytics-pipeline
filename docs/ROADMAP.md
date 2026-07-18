# Roadmap

## Completed

- **v0.1** — Repository foundation, scaffold, CI placeholder, git workflow
- **v0.2** — Deterministic synthetic data generation (campaigns, products, impressions, clicks, costs, conversions)
- **v0.3** — DuckDB raw ingestion, raw data validation, SQL staging and analytical marts, metric quality tests
- **v0.4** — Markdown performance report and rule-based analytics assistant
- **v0.5** — Portfolio consistency: metric realism, PLN currency, fact table grain clarification, consolidated insights, documentation alignment
- **v0.6** — End-to-end pipeline orchestrator (`src/run_pipeline.py`) and GitHub Actions CI hardening (tests + end-to-end jobs)

## Current

- **v0.6** is the current stable state of `develop`.

## Planned

- Prefect orchestration
- Streamlit dashboard for interactive exploration
- Optional Ollama integration (local LLM-based insight generation)
- BigQuery-compatible SQL transformations
- Cloud deployment reference
- Stable **v1.0** portfolio release (tagged, documented, end-to-end CI passing)
