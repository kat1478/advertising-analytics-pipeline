# Architecture Decisions

## ADR-001: Use DuckDB as the local analytical warehouse

DuckDB is used to keep the project lightweight, reproducible, and SQL-first. It allows the project to mimic analytical warehouse workflows without requiring cloud infrastructure.

## ADR-002: Keep SQL transformations in versioned files

SQL files live under `sql/staging/` and `sql/marts/`. This makes analytical logic easy to review and closer to real analytics engineering workflows.

## ADR-003: Generate synthetic data instead of using real ad data

Synthetic data avoids privacy and licensing risks while still allowing realistic campaign, product, click, cost, and conversion relationships.

## ADR-004: Keep private agent instructions out of the repository

Antigravity prompts, skills, task handoffs, and local notes are ignored by git. The public repository should contain only professional project artifacts.
