import duckdb
from src.load_raw import load_raw_data
from src.generate_data import main as generate_data_main

def test_load_raw_data(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    generate_data_main(output_dir=raw_dir)
    
    db_path = tmp_path / "warehouse.duckdb"
    
    load_raw_data(db_path=db_path, raw_dir=raw_dir)
    
    conn = duckdb.connect(str(db_path))
    
    tables_result = conn.execute("SHOW TABLES").fetchall()
    tables = [t[0] for t in tables_result]
    
    expected_tables = [
        'raw_campaigns',
        'raw_products',
        'raw_impressions',
        'raw_clicks',
        'raw_costs',
        'raw_conversions'
    ]
    
    for t in expected_tables:
        assert t in tables, f"Table {t} should exist in duckdb"
        
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        assert count > 0, f"Table {t} should not be empty"
        
    conn.close()
