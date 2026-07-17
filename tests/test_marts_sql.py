import duckdb
import pytest
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.run_sql import execute_sql_files
from src.paths import PROJECT_ROOT

@pytest.fixture
def setup_db(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    generate_data_main(output_dir=raw_dir)
    
    db_path = tmp_path / "ads.duckdb"
    load_raw_data(db_path=db_path, raw_dir=raw_dir)
    
    sql_dir = PROJECT_ROOT / "sql"
    execute_sql_files(db_path=db_path, sql_dir=sql_dir)
    
    return db_path

def test_marts_tables_exist(setup_db):
    conn = duckdb.connect(str(setup_db))
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    conn.close()
    
    expected_tables = [
        'dim_campaigns', 'dim_products', 'fact_campaign_product_daily',
        'daily_campaign_performance', 'category_performance'
    ]
    for t in expected_tables:
        assert t in tables, f"{t} should exist"
    # Verify old table name is not accidentally present
    assert 'fact_ad_events' not in tables, "old fact_ad_events table should not exist"

def test_marts_tables_not_empty(setup_db):
    conn = duckdb.connect(str(setup_db))
    tables = [
        'dim_campaigns', 'dim_products', 'fact_campaign_product_daily',
        'daily_campaign_performance', 'category_performance'
    ]
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        assert count > 0, f"{t} should not be empty"
    conn.close()

def test_daily_campaign_performance_metrics(setup_db):
    conn = duckdb.connect(str(setup_db))
    res = conn.execute("SELECT ctr, conversion_rate, cpc, roas FROM daily_campaign_performance").fetchall()
    for row in res:
        ctr, conv_rate, cpc, roas = row
        if ctr is not None:
            assert 0 <= ctr <= 1, "CTR must be between 0 and 1"
        if conv_rate is not None:
            assert 0 <= conv_rate <= 1, "Conversion rate must be between 0 and 1"
        if cpc is not None:
            assert cpc >= 0, "CPC must be non-negative"
        if roas is not None:
            assert roas >= 0, "ROAS must be non-negative"
    conn.close()

def test_no_duplicate_rows_daily_campaign(setup_db):
    conn = duckdb.connect(str(setup_db))
    dups = conn.execute("SELECT COUNT(*) FROM (SELECT event_date, campaign_id, COUNT(*) FROM daily_campaign_performance GROUP BY 1, 2 HAVING COUNT(*) > 1)").fetchone()[0]
    assert dups == 0, "Duplicate rows in daily_campaign_performance"
    conn.close()

def test_no_duplicate_rows_category(setup_db):
    conn = duckdb.connect(str(setup_db))
    dups = conn.execute("SELECT COUNT(*) FROM (SELECT category, COUNT(*) FROM category_performance GROUP BY 1 HAVING COUNT(*) > 1)").fetchone()[0]
    assert dups == 0, "Duplicate rows in category_performance"
    conn.close()
