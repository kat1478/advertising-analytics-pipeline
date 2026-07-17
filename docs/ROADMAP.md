# Roadmap

## Completed

- **v0.1** — Repository foundation, scaffold, CI placeholder, git workflow
- **v0.2** — Deterministic synthetic data generation (campaigns, products, impressions, clicks, costs, conversions)
- **v0.3** — DuckDB raw ingestion, raw data validation, SQL staging and analytical marts, metric quality tests
- **v0.4** — Markdown performance report and rule-based analytics assistant
- **v0.5** — Portfolio consistency: metric realism, PLN currency, fact table grain clarification, consolidated insights, documentation alignment

## Current

- **v0.5** is the current stable state of `develop`.

## Planned

- End-to-end pipeline orchestrator (unified runner for all steps)
- GitHub Actions hardening (full pipeline CI on every PR)
- Prefect orchestration
- Streamlit dashboard for interactive exploration
- Optional Ollama integration (local LLM-based insight generation)
- BigQuery-compatible SQL transformations
- Cloud deployment reference
- Stable **v1.0** portfolio release (tagged, documented, end-to-end CI passing)
