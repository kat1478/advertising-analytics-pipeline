"""Tests for the end-to-end pipeline orchestrator (src/run_pipeline.py).

All tests use temporary directories so they do not read from or write to the
committed repository database, raw CSV files, or report artifacts.

Test isolation strategy:
  - tmp_path / tmp_path_factory provide unique temp directories per test
  - a module-scoped fixture runs the pipeline once for the majority of tests
    (avoiding redundant regeneration)
  - the failure-propagation test uses a separate invocation with a bad path
"""
import duckdb
import pytest
from pathlib import Path

import src.run_pipeline as run_pipeline_module
from src.run_pipeline import run_pipeline, _RAW_TABLES, _STAGING_TABLES, _MART_TABLES
from src.paths import PROJECT_ROOT
from src.config import CURRENCY_SYMBOL, CURRENCY_CODE


# ── Shared fixture: run the pipeline once for all read-only tests ─────────────

@pytest.fixture(scope="module")
def pipeline_outputs(tmp_path_factory):
    """Run the full pipeline in a temporary workspace and return the paths."""
    base = tmp_path_factory.mktemp("pipeline_run")
    raw_dir = base / "raw"
    raw_dir.mkdir()
    db_path = base / "ads.duckdb"
    report_dir = base / "reports"
    report_dir.mkdir()

    run_pipeline(
        raw_dir=raw_dir,
        db_path=db_path,
        sql_dir=PROJECT_ROOT / "sql",
        report_dir=report_dir,
    )
    return {"raw_dir": raw_dir, "db_path": db_path, "report_dir": report_dir}


# ── Import and callable checks ────────────────────────────────────────────────

def test_run_pipeline_module_importable():
    """The module must be importable without side effects."""
    assert hasattr(run_pipeline_module, "run_pipeline"), (
        "run_pipeline_module must expose a 'run_pipeline' callable"
    )


def test_run_pipeline_is_callable():
    assert callable(run_pipeline), "run_pipeline must be a callable function"


# ── Full pipeline ─────────────────────────────────────────────────────────────

def test_run_pipeline_completes(pipeline_outputs):
    """The pipeline must complete without raising an exception."""
    # If the fixture ran successfully, this test trivially passes.
    assert pipeline_outputs["db_path"].exists()


# ── Table verification ────────────────────────────────────────────────────────

def test_run_pipeline_all_tables_present(pipeline_outputs):
    """All raw, staging and mart tables must exist after the pipeline run."""
    conn = duckdb.connect(str(pipeline_outputs["db_path"]))
    try:
        present = {t[0] for t in conn.execute("SHOW TABLES").fetchall()}
    finally:
        conn.close()

    for table in _RAW_TABLES + _STAGING_TABLES + _MART_TABLES:
        assert table in present, f"Expected table missing after pipeline run: {table}"


def test_run_pipeline_fact_table_name(pipeline_outputs):
    """fact_campaign_product_daily must exist; fact_ad_events must not."""
    conn = duckdb.connect(str(pipeline_outputs["db_path"]))
    try:
        present = {t[0] for t in conn.execute("SHOW TABLES").fetchall()}
    finally:
        conn.close()

    assert "fact_campaign_product_daily" in present, (
        "fact_campaign_product_daily must exist after pipeline run"
    )
    assert "fact_ad_events" not in present, (
        "Deprecated 'fact_ad_events' must not exist — was it re-created?"
    )


# ── Report file checks ────────────────────────────────────────────────────────

def test_run_pipeline_reports_exist(pipeline_outputs):
    """Both report files must exist and be non-empty."""
    report_dir = pipeline_outputs["report_dir"]
    for filename in ["campaign_report.md", "analytics_insights.md"]:
        path = report_dir / filename
        assert path.exists(), f"Report file missing: {filename}"
        assert path.stat().st_size > 0, f"Report file is empty: {filename}"


def test_run_pipeline_reports_pln_currency(pipeline_outputs):
    """Reports must use PLN currency and must not use '$' as a currency marker."""
    report_dir = pipeline_outputs["report_dir"]
    for filename in ["campaign_report.md", "analytics_insights.md"]:
        content = (report_dir / filename).read_text(encoding="utf-8")
        assert CURRENCY_SYMBOL in content or CURRENCY_CODE in content, (
            f"{filename} must reference PLN currency"
        )
        assert "$ " not in content and "$\n" not in content, (
            f"{filename} must not use '$' as a currency marker"
        )


def test_run_pipeline_reports_no_placeholder(pipeline_outputs):
    """Reports must not contain TODO placeholder text."""
    report_dir = pipeline_outputs["report_dir"]
    for filename in ["campaign_report.md", "analytics_insights.md"]:
        content = (report_dir / filename).read_text(encoding="utf-8")
        assert "TODO" not in content, f"{filename} contains placeholder text 'TODO'"


def test_run_pipeline_reports_no_dynamic_timestamp(pipeline_outputs):
    """Reports must not embed a runtime-generated timestamp."""
    report_dir = pipeline_outputs["report_dir"]
    for filename in ["campaign_report.md", "analytics_insights.md"]:
        content = (report_dir / filename).read_text(encoding="utf-8")
        assert "Generated At:" not in content, (
            f"{filename} must use deterministic metadata, not a runtime timestamp"
        )


def test_run_pipeline_reports_deterministic_metadata(pipeline_outputs):
    """Reports must contain the deterministic dataset metadata (seed + period)."""
    report_dir = pipeline_outputs["report_dir"]
    for filename in ["campaign_report.md", "analytics_insights.md"]:
        content = (report_dir / filename).read_text(encoding="utf-8")
        assert "Dataset Seed:" in content or "Seed" in content, (
            f"{filename} must contain deterministic seed metadata"
        )
        assert "Reporting Period:" in content or "2023-06" in content, (
            f"{filename} must contain a reporting period reference"
        )


# ── Determinism ───────────────────────────────────────────────────────────────

def test_run_pipeline_reports_deterministic(tmp_path_factory):
    """Running the pipeline twice with the same seed must produce identical reports."""
    def run_once(label: str):
        base = tmp_path_factory.mktemp(f"det_{label}")
        raw_dir = base / "raw"
        raw_dir.mkdir()
        report_dir = base / "reports"
        report_dir.mkdir()
        run_pipeline(
            raw_dir=raw_dir,
            db_path=base / "ads.duckdb",
            sql_dir=PROJECT_ROOT / "sql",
            report_dir=report_dir,
        )
        return report_dir

    dir1 = run_once("a")
    dir2 = run_once("b")

    for filename in ["campaign_report.md", "analytics_insights.md"]:
        content1 = (dir1 / filename).read_text(encoding="utf-8")
        content2 = (dir2 / filename).read_text(encoding="utf-8")
        assert content1 == content2, (
            f"{filename} is not deterministic — two runs produced different output"
        )


# ── Error propagation ─────────────────────────────────────────────────────────

def test_run_pipeline_failure_propagated(tmp_path):
    """A step failure must propagate as an exception, not be silently swallowed."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    # Provide a database path inside a non-existent parent on a read-only
    # location — this will cause load_raw to fail because DuckDB cannot open
    # a file when the CSV sources are missing (raw_dir is empty after generate
    # fails, but generate itself won't fail; instead omit raw CSVs by using
    # an empty raw_dir and pointing db_path into a read-only spot).
    #
    # Simpler approach: use a non-writable db directory.
    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(0o444)  # read-only

    bad_db_path = readonly_dir / "ads.duckdb"

    with pytest.raises(Exception):
        run_pipeline(
            raw_dir=raw_dir,
            db_path=bad_db_path,
            sql_dir=PROJECT_ROOT / "sql",
            report_dir=tmp_path / "reports",
        )
