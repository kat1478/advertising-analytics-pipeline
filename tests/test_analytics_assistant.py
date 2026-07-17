import pytest
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.run_sql import execute_sql_files
from src.analytics_assistant import generate_insights
from src.paths import PROJECT_ROOT

@pytest.fixture(scope="module")
def setup_pipeline(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("assistant_pipeline")
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    generate_data_main(output_dir=raw_dir)
    
    db_path = tmp_path / "ads.duckdb"
    load_raw_data(db_path=db_path, raw_dir=raw_dir)
    
    sql_dir = PROJECT_ROOT / "sql"
    execute_sql_files(db_path=db_path, sql_dir=sql_dir)
    
    report_dir = tmp_path / "reports"
    return db_path, report_dir

def test_analytics_assistant(setup_pipeline):
    db_path, report_dir = setup_pipeline
    
    generate_insights(db_path=db_path, output_dir=report_dir)
    
    insight_path = report_dir / "analytics_insights.md"
    assert insight_path.exists(), "Insights file was not created"
    
    content = insight_path.read_text(encoding="utf-8")
    
    assert len(content) > 0, "Insights file is empty"
    assert "TODO" not in content, "Output contains placeholder text"
    
    assert "## Campaign Insights" in content
    assert "## Category Insights" in content
    assert "## Suggested Actions" in content
    assert "## Limitations" in content
    
    # Check if there is at least one campaign or category name insight (Campaign_X or category names)
    assert "Campaign_" in content or "Electronics" in content or "Clothing" in content or "Home" in content or "Sports" in content or "Toys" in content
    
    # Check deterministic run
    generate_insights(db_path=db_path, output_dir=report_dir)
    content2 = insight_path.read_text(encoding="utf-8")
    
    # We strip the "Generated At" timestamp for deterministic comparison
    lines1 = [line for line in content.splitlines() if "Generated At:" not in line]
    lines2 = [line for line in content2.splitlines() if "Generated At:" not in line]
    
    assert lines1 == lines2, "Assistant is not deterministic"
