"""End-to-end pipeline orchestrator for the Advertising Analytics Data Pipeline.

Executes every pipeline step in the required order:

  1. Generate synthetic data
  2. Load raw data into DuckDB
  3. Validate raw data
  4. Build staging and mart models
  5. Generate performance report
  6. Generate analytics insights
  7. Verify outputs

Usage:
    python -m src.run_pipeline

Design notes:
- All steps are called via their Python API (no subprocesses).
- Path arguments are injected so the function is fully testable with
  temporary directories.
- Exceptions from any step are re-raised immediately; the orchestrator
  does NOT suppress failures.
- sys.exit() is called only from __main__, not from run_pipeline() itself.
"""
import logging
import sys
import duckdb
from pathlib import Path

from src.paths import RAW_DATA_DIR, DATABASE_PATH, PROJECT_ROOT, REPORTS_DIR
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.validate_data import run_validations
from src.run_sql import execute_sql_files
from src.generate_report import generate_report
from src.analytics_assistant import generate_insights

logger = logging.getLogger(__name__)

# ── Expected tables ────────────────────────────────────────────────────────────
_RAW_TABLES = [
    "raw_campaigns",
    "raw_products",
    "raw_impressions",
    "raw_clicks",
    "raw_costs",
    "raw_conversions",
]

_STAGING_TABLES = [
    "stg_campaigns",
    "stg_products",
    "stg_impressions",
    "stg_clicks",
    "stg_costs",
    "stg_conversions",
]

_MART_TABLES = [
    "dim_campaigns",
    "dim_products",
    "fact_campaign_product_daily",
    "daily_campaign_performance",
    "category_performance",
]

_REPORT_FILES = [
    "campaign_report.md",
    "analytics_insights.md",
]


def _verify_outputs(db_path: Path, report_dir: Path) -> None:
    """Step 7: verify that all expected outputs were produced.

    Raises RuntimeError with a descriptive message on the first failed check.
    """
    # ── Database file ──
    if not db_path.exists():
        raise RuntimeError(f"DuckDB database not found: {db_path}")

    # ── Tables ──
    conn = duckdb.connect(str(db_path))
    try:
        present = {t[0] for t in conn.execute("SHOW TABLES").fetchall()}
    finally:
        conn.close()

    for table in _RAW_TABLES + _STAGING_TABLES + _MART_TABLES:
        if table not in present:
            raise RuntimeError(f"Expected table missing from DuckDB: {table}")

    if "fact_ad_events" in present:
        raise RuntimeError(
            "Deprecated table 'fact_ad_events' is still present. "
            "It should have been replaced by 'fact_campaign_product_daily'."
        )

    # ── Report files ──
    for filename in _REPORT_FILES:
        path = report_dir / filename
        if not path.exists():
            raise RuntimeError(f"Expected report file not found: {path}")
        if path.stat().st_size == 0:
            raise RuntimeError(f"Report file is empty: {path}")
        if "TODO" in path.read_text(encoding="utf-8"):
            raise RuntimeError(f"Report file contains placeholder 'TODO': {path}")

    logger.info("Output verification passed.")


def run_pipeline(
    raw_dir: Path = RAW_DATA_DIR,
    db_path: Path = DATABASE_PATH,
    sql_dir: Path = PROJECT_ROOT / "sql",
    report_dir: Path = REPORTS_DIR,
) -> None:
    """Execute the full advertising analytics pipeline.

    Args:
        raw_dir:    Directory where synthetic CSV files are written.
        db_path:    Path to the DuckDB database file.
        sql_dir:    Directory containing staging/ and marts/ SQL sub-directories.
        report_dir: Directory where Markdown reports are written.

    Raises:
        RuntimeError: If raw data validation fails.
        Exception:    Any exception from a downstream step is re-raised unchanged.
    """
    # Ensure output directories exist before any step writes to them.
    raw_dir.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    steps = [
        ("1. Generate synthetic data",        lambda: generate_data_main(output_dir=raw_dir)),
        ("2. Load raw data into DuckDB",       lambda: load_raw_data(db_path=db_path, raw_dir=raw_dir)),
        ("3. Validate raw data",               None),   # handled specially below
        ("4. Build staging and mart models",   lambda: execute_sql_files(db_path=db_path, sql_dir=sql_dir)),
        ("5. Generate performance report",     lambda: generate_report(db_path=db_path, report_dir=report_dir)),
        ("6. Generate analytics insights",     lambda: generate_insights(db_path=db_path, output_dir=report_dir)),
        ("7. Verify outputs",                  lambda: _verify_outputs(db_path=db_path, report_dir=report_dir)),
    ]

    for label, fn in steps:
        logger.info(f"── {label} ──")

        # Step 3 (validation) has special return-value handling.
        if label.startswith("3."):
            try:
                results = run_validations(db_path=db_path)
            except Exception:
                logger.error(f"Step failed: {label}")
                raise
            if results["failed"]:
                failed_msgs = ", ".join(results["failed"])
                raise RuntimeError(
                    f"Raw data validation failed — checks that did not pass: {failed_msgs}"
                )
            continue

        try:
            fn()
        except Exception:
            logger.error(f"Step failed: {label}")
            raise


def _print_summary(raw_dir: Path, db_path: Path, report_dir: Path) -> None:
    logger.info("=" * 60)
    logger.info("Pipeline completed successfully.")
    logger.info(f"  Database : {db_path}")
    logger.info(f"  Reports  : {report_dir}")
    logger.info(f"  Tables   : {len(_RAW_TABLES)} raw  |  "
                f"{len(_STAGING_TABLES)} staging  |  "
                f"{len(_MART_TABLES)} marts")
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        run_pipeline()
        _print_summary(RAW_DATA_DIR, DATABASE_PATH, REPORTS_DIR)
    except Exception as exc:
        logger.error(f"Pipeline failed: {exc}")
        sys.exit(1)
