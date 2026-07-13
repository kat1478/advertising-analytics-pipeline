import duckdb
import logging
from pathlib import Path
from src.paths import DATABASE_PATH, PROJECT_ROOT

logger = logging.getLogger(__name__)

def execute_sql_files(db_path=DATABASE_PATH, sql_dir=PROJECT_ROOT / "sql"):
    conn = duckdb.connect(str(db_path))
    try:
        staging_dir = sql_dir / "staging"
        if staging_dir.exists():
            staging_order = [
                "stg_campaigns.sql",
                "stg_products.sql",
                "stg_impressions.sql",
                "stg_clicks.sql",
                "stg_costs.sql",
                "stg_conversions.sql"
            ]
            for file_name in staging_order:
                file_path = staging_dir / file_name
                if file_path.exists():
                    logger.info(f"Executing {file_path.name} (staging)")
                    with open(file_path, "r", encoding="utf-8") as f:
                        conn.execute(f.read())
        
        marts_dir = sql_dir / "marts"
        if marts_dir.exists():
            marts_order = [
                "dim_campaigns.sql",
                "dim_products.sql",
                "fact_ad_events.sql",
                "daily_campaign_performance.sql",
                "category_performance.sql"
            ]
            for file_name in marts_order:
                file_path = marts_dir / file_name
                if file_path.exists():
                    logger.info(f"Executing {file_path.name} (marts)")
                    with open(file_path, "r", encoding="utf-8") as f:
                        conn.execute(f.read())
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Starting SQL execution...")
    execute_sql_files()
    logger.info("SQL execution finished.")
