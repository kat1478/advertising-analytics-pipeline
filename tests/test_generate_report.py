import pytest
from pathlib import Path
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.run_sql import execute_sql_files
from src.generate_report import generate_report
from src.paths import PROJECT_ROOT

@pytest.fixture(scope="module")
def setup_pipeline(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("report_pipeline")
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    generate_data_main(output_dir=raw_dir)
    
    db_path = tmp_path / "ads.duckdb"
    load_raw_data(db_path=db_path, raw_dir=raw_dir)
    
    sql_dir = PROJECT_ROOT / "sql"
    execute_sql_files(db_path=db_path, sql_dir=sql_dir)
    
    report_dir = tmp_path / "reports"
    return db_path, report_dir

def test_generate_report(setup_pipeline):
    db_path, report_dir = setup_pipeline
    
    generate_report(db_path=db_path, report_dir=report_dir)
    
    report_path = report_dir / "campaign_report.md"
    assert report_path.exists(), "Report file was not created"
    
    content = report_path.read_text(encoding="utf-8")
    
    assert len(content) > 0, "Report is empty"
    assert "TODO" not in content, "Report contains placeholder text"
    
    assert "## Executive Summary" in content
    assert "## Top Campaigns" in content
    assert "## Underperforming Campaigns" in content
    assert "## Category Performance" in content
    assert "## Data Quality Notes" in content
    assert "## Interpretation Notes" in content
    
    assert "Campaign_" in content or "Electronics" in content or "Clothing" in content or "Home" in content or "Sports" in content or "Toys" in content


def test_report_no_dynamic_timestamp(setup_pipeline):
    """Committed report must not include a runtime-generated timestamp."""
    db_path, report_dir = setup_pipeline
    generate_report(db_path=db_path, report_dir=report_dir)
    content = (report_dir / "campaign_report.md").read_text(encoding="utf-8")
    assert "Generated At:" not in content, (
        "Report must use deterministic metadata (seed/period), not a runtime timestamp"
    )


def test_report_uses_pln_currency(setup_pipeline):
    """Report must use PLN symbol and must not use '$' as a currency marker."""
    from src.config import CURRENCY_SYMBOL
    db_path, report_dir = setup_pipeline
    generate_report(db_path=db_path, report_dir=report_dir)
    content = (report_dir / "campaign_report.md").read_text(encoding="utf-8")

    assert CURRENCY_SYMBOL in content, f"Expected '{CURRENCY_SYMBOL}' in report"
    assert "$ " not in content and "$\n" not in content, (
        "Report must not use '$' as a currency symbol"
    )
