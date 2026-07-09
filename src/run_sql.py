import duckdb
import logging
from pathlib import Path
from src.paths import DATABASE_PATH, PROJECT_ROOT

logger = logging.getLogger(__name__)

def execute_sql_files(db_path=DATABASE_PATH, sql_dir=PROJECT_ROOT / "sql" / "staging"):
    if not sql_dir.exists():
        logger.warning(f"SQL directory {sql_dir} does not exist.")
        return

    sql_files = sorted(sql_dir.glob("*.sql"))
    if not sql_files:
        logger.warning(f"No SQL files found in {sql_dir}.")
        return

    conn = duckdb.connect(str(db_path))
    
    try:
        for file_path in sql_files:
            logger.info(f"Executing {file_path.name}")
            with open(file_path, "r", encoding="utf-8") as f:
                query = f.read()
            conn.execute(query)
            logger.info(f"Successfully executed {file_path.name}")
    finally:
        conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Starting SQL execution...")
    execute_sql_files()
    logger.info("SQL execution finished.")
