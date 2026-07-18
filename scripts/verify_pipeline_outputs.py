#!/usr/bin/env python3
"""CI smoke-check: verify that the pipeline produced all expected outputs.

Run after `python -m src.run_pipeline` in CI to confirm that:
  - the DuckDB database was created
  - all expected raw, staging and mart tables are present
  - the deprecated fact_ad_events table is absent
  - both Markdown report files exist and are non-empty
  - reports contain PLN currency marker (sanity check for economic calibration)
  - reports do not contain TODO placeholder text

Exits with code 0 on success, code 1 on the first failed check.

Usage (from repository root):
    python scripts/verify_pipeline_outputs.py
    python scripts/verify_pipeline_outputs.py --db-path database/ads.duckdb --reports-dir reports

This script intentionally does NOT re-run the test suite.
"""
import argparse
import sys
import duckdb
from pathlib import Path

# ---------------------------------------------------------------------------
# Expected table inventory
# ---------------------------------------------------------------------------
RAW_TABLES = [
    "raw_campaigns",
    "raw_products",
    "raw_impressions",
    "raw_clicks",
    "raw_costs",
    "raw_conversions",
]

STAGING_TABLES = [
    "stg_campaigns",
    "stg_products",
    "stg_impressions",
    "stg_clicks",
    "stg_costs",
    "stg_conversions",
]

MART_TABLES = [
    "dim_campaigns",
    "dim_products",
    "fact_campaign_product_daily",
    "daily_campaign_performance",
    "category_performance",
]

REPORT_FILES = [
    "campaign_report.md",
    "analytics_insights.md",
]

DEPRECATED_TABLES = ["fact_ad_events"]


def _fail(message: str) -> None:
    print(f"[FAIL] {message}", file=sys.stderr)
    sys.exit(1)


def _ok(message: str) -> None:
    print(f"[OK]   {message}")


def verify(db_path: Path, reports_dir: Path) -> None:
    print(f"Verifying pipeline outputs...")
    print(f"  Database : {db_path}")
    print(f"  Reports  : {reports_dir}")
    print()

    # ── 1. Database file exists ──
    if not db_path.exists():
        _fail(f"DuckDB database not found: {db_path}")
    _ok(f"Database exists: {db_path.name}")

    # ── 2. Table checks ──
    conn = duckdb.connect(str(db_path))
    try:
        present = {t[0] for t in conn.execute("SHOW TABLES").fetchall()}
    finally:
        conn.close()

    all_expected = RAW_TABLES + STAGING_TABLES + MART_TABLES
    for table in all_expected:
        if table not in present:
            _fail(f"Expected table missing: {table}")
        _ok(f"Table present: {table}")

    for table in DEPRECATED_TABLES:
        if table in present:
            _fail(
                f"Deprecated table still present: {table}. "
                "This should have been replaced by 'fact_campaign_product_daily'."
            )
    _ok("Deprecated tables absent")

    # ── 3. Report files ──
    for filename in REPORT_FILES:
        path = reports_dir / filename
        if not path.exists():
            _fail(f"Report file missing: {path}")
        if path.stat().st_size == 0:
            _fail(f"Report file is empty: {path}")
        content = path.read_text(encoding="utf-8")
        if "TODO" in content:
            _fail(f"Report contains 'TODO' placeholder: {path}")
        if "PLN" not in content and "zł" not in content:
            _fail(f"Report does not reference PLN currency: {path}")
        _ok(f"Report valid: {filename}")

    print()
    print("All checks passed.")


def main() -> None:
    repo_root = Path(__file__).parent.parent.resolve()

    parser = argparse.ArgumentParser(description="Verify pipeline outputs.")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=repo_root / "database" / "ads.duckdb",
        help="Path to the DuckDB database file.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=repo_root / "reports",
        help="Directory containing the generated Markdown reports.",
    )
    args = parser.parse_args()

    verify(db_path=args.db_path, reports_dir=args.reports_dir)


if __name__ == "__main__":
    main()
