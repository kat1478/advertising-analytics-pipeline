import duckdb
import logging
from pathlib import Path
from src.paths import RAW_DATA_DIR, DATABASE_PATH

logger = logging.getLogger(__name__)

def load_raw_data(db_path=DATABASE_PATH, raw_dir=RAW_DATA_DIR):
    logger.info(f"Connecting to DuckDB at {db_path}")
    conn = duckdb.connect(str(db_path))
    
    csv_files = {
        'raw_campaigns': 'campaigns.csv',
        'raw_products': 'products.csv',
        'raw_impressions': 'impressions.csv',
        'raw_clicks': 'clicks.csv',
        'raw_costs': 'costs.csv',
        'raw_conversions': 'conversions.csv'
    }
    
    for table_name, file_name in csv_files.items():
        file_path = raw_dir / file_name
        if not file_path.exists():
            logger.warning(f"File {file_path} not found. Skipping {table_name}.")
            continue
            
        logger.info(f"Loading {file_path} into {table_name}")
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        # Note: escaping the path for DuckDB
        conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
        
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        logger.info(f"Successfully loaded {count} rows into {table_name}")
        
    conn.close()
    logger.info("Raw data load complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    load_raw_data()
