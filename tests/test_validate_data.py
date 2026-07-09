import duckdb
import pytest
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.validate_data import run_validations

@pytest.fixture
def setup_db(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    generate_data_main(output_dir=raw_dir)
    
    db_path = tmp_path / "ads.duckdb"
    load_raw_data(db_path=db_path, raw_dir=raw_dir)
    return db_path

def test_validation_passes(setup_db):
    results = run_validations(db_path=setup_db)
    assert len(results['failed']) == 0
    assert len(results['passed']) > 0

def test_missing_table(setup_db):
    conn = duckdb.connect(str(setup_db))
    conn.execute("DROP TABLE raw_campaigns")
    conn.close()
    
    results = run_validations(db_path=setup_db)
    assert "Table raw_campaigns exists" in results['failed']

def test_duplicate_pk(setup_db):
    conn = duckdb.connect(str(setup_db))
    conn.execute("INSERT INTO raw_campaigns SELECT * FROM raw_campaigns LIMIT 1")
    conn.close()
    
    results = run_validations(db_path=setup_db)
    assert "PK raw_campaigns.campaign_id unique" in results['failed']

def test_negative_cost(setup_db):
    conn = duckdb.connect(str(setup_db))
    conn.execute("UPDATE raw_costs SET cost = -1.0 WHERE rowid = 0")
    conn.close()
    
    results = run_validations(db_path=setup_db)
    assert "Numeric raw_costs.cost >= 0" in results['failed']

def test_broken_fk(setup_db):
    conn = duckdb.connect(str(setup_db))
    conn.execute("INSERT INTO raw_clicks (click_id, impression_id, campaign_id, product_id, event_timestamp) VALUES ('ck_bad', 'imp_none', 'c', 'p', '2023-01-01 00:00:00')")
    conn.close()
    
    results = run_validations(db_path=setup_db)
    assert "FK raw_clicks -> raw_impressions" in results['failed']
