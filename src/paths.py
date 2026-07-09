from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "ads.duckdb"

REPORTS_DIR = PROJECT_ROOT / "reports"

SQL_DIR = PROJECT_ROOT / "sql"
STAGING_SQL_DIR = SQL_DIR / "staging"
MARTS_SQL_DIR = SQL_DIR / "marts"
