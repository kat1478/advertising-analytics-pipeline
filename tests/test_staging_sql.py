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
    
    sql_dir = PROJECT_ROOT / "sql" / "staging"
    execute_sql_files(db_path=db_path, sql_dir=sql_dir)
    
    return db_path

def test_staging_tables_exist(setup_db):
    conn = duckdb.connect(str(setup_db))
    tables = [t[0] for t in conn.execute("SHOW TABLES").fetchall()]
    conn.close()
    
    expected_tables = [
        'stg_campaigns', 'stg_products', 'stg_impressions', 
        'stg_clicks', 'stg_costs', 'stg_conversions'
    ]
    for t in expected_tables:
        assert t in tables, f"{t} should exist"

def test_staging_tables_not_empty(setup_db):
    conn = duckdb.connect(str(setup_db))
    tables = [
        'stg_campaigns', 'stg_products', 'stg_impressions', 
        'stg_clicks', 'stg_costs', 'stg_conversions'
    ]
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        assert count > 0, f"{t} should not be empty"
    conn.close()

def test_duplicate_pk_not_introduced(setup_db):
    conn = duckdb.connect(str(setup_db))
    
    dups = conn.execute("SELECT COUNT(campaign_id) - COUNT(DISTINCT campaign_id) FROM stg_campaigns").fetchone()[0]
    assert dups == 0, "Duplicate PK in stg_campaigns"
    
    dups = conn.execute("SELECT COUNT(product_id) - COUNT(DISTINCT product_id) FROM stg_products").fetchone()[0]
    assert dups == 0, "Duplicate PK in stg_products"
    
    conn.close()

def test_expected_columns(setup_db):
    conn = duckdb.connect(str(setup_db))
    
    cols = [c[0] for c in conn.execute("DESCRIBE stg_impressions").fetchall()]
    assert 'event_date' in cols
    
    cols = [c[0] for c in conn.execute("DESCRIBE stg_clicks").fetchall()]
    assert 'event_date' in cols
    
    cols = [c[0] for c in conn.execute("DESCRIBE stg_conversions").fetchall()]
    assert 'event_date' in cols
    
    conn.close()
