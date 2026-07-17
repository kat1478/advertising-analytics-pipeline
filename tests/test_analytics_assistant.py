import pytest
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.run_sql import execute_sql_files
from src.analytics_assistant import generate_insights
from src.config import (
    CURRENCY_SYMBOL,
    LOW_ROAS_THRESHOLD,
    HIGH_ROAS_THRESHOLD,
    EXCEPTIONAL_ROAS_THRESHOLD,
)
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


def test_analytics_assistant_creates_file(setup_pipeline):
    db_path, report_dir = setup_pipeline
    generate_insights(db_path=db_path, output_dir=report_dir)

    insight_path = report_dir / "analytics_insights.md"
    assert insight_path.exists(), "Insights file was not created"

    content = insight_path.read_text(encoding="utf-8")
    assert len(content) > 0, "Insights file is empty"
    assert "TODO" not in content, "Output contains placeholder text"


def test_analytics_assistant_required_sections(setup_pipeline):
    db_path, report_dir = setup_pipeline
    generate_insights(db_path=db_path, output_dir=report_dir)
    content = (report_dir / "analytics_insights.md").read_text(encoding="utf-8")

    assert "## Campaign Insights" in content
    assert "## Category Insights" in content
    assert "## Limitations" in content
    assert "## Threshold Reference" in content


def test_analytics_assistant_no_dynamic_timestamp(setup_pipeline):
    db_path, report_dir = setup_pipeline
    generate_insights(db_path=db_path, output_dir=report_dir)
    content = (report_dir / "analytics_insights.md").read_text(encoding="utf-8")

    assert "Generated At:" not in content, (
        "Committed insight artifact must not contain a dynamic runtime timestamp"
    )


def test_analytics_assistant_uses_pln_currency(setup_pipeline):
    db_path, report_dir = setup_pipeline
    generate_insights(db_path=db_path, output_dir=report_dir)
    content = (report_dir / "analytics_insights.md").read_text(encoding="utf-8")

    assert CURRENCY_SYMBOL in content, f"Expected currency symbol '{CURRENCY_SYMBOL}' in output"
    # Dollar sign must not appear as a currency marker in the report body
    assert "$ " not in content and "$\n" not in content, (
        "Report must not use '$' as a currency symbol"
    )


def test_analytics_assistant_one_insight_per_campaign(setup_pipeline):
    """Each campaign name must appear at most once in the Campaign Insights section."""
    db_path, report_dir = setup_pipeline
    generate_insights(db_path=db_path, output_dir=report_dir)
    content = (report_dir / "analytics_insights.md").read_text(encoding="utf-8")

    # Extract campaign insight section
    sections = content.split("## Category Insights")
    campaign_section = sections[0] if len(sections) > 1 else content

    # Count occurrences of bold campaign name patterns like **Campaign_X**
    import re
    names = re.findall(r"\*\*(Campaign_\d+)\*\*", campaign_section)
    seen = set()
    for name in names:
        assert name not in seen, (
            f"{name} appears more than once in Campaign Insights — "
            f"consolidated single-insight rule violated"
        )
        seen.add(name)


def test_analytics_assistant_valid_classifications(setup_pipeline):
    """All classification labels used must be in the allowed set."""
    db_path, report_dir = setup_pipeline
    generate_insights(db_path=db_path, output_dir=report_dir)
    content = (report_dir / "analytics_insights.md").read_text(encoding="utf-8")

    valid_labels = {"Critical", "Warning", "Monitor", "Opportunity"}
    import re
    found_labels = set(re.findall(r"— (\w+):", content))
    unexpected = found_labels - valid_labels
    assert not unexpected, f"Unexpected classification labels found: {unexpected}"


def test_analytics_assistant_is_deterministic(setup_pipeline):
    """Running the assistant twice on the same database must produce identical output."""
    db_path, report_dir = setup_pipeline
    generate_insights(db_path=db_path, output_dir=report_dir)
    content1 = (report_dir / "analytics_insights.md").read_text(encoding="utf-8")

    generate_insights(db_path=db_path, output_dir=report_dir)
    content2 = (report_dir / "analytics_insights.md").read_text(encoding="utf-8")

    assert content1 == content2, "Assistant output is not deterministic"
