from src.paths import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    DATABASE_DIR,
    REPORTS_DIR,
    SQL_DIR,
    STAGING_SQL_DIR,
    MARTS_SQL_DIR
)

def test_directories_exist():
    expected_dirs = [
        PROJECT_ROOT,
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        DATABASE_DIR,
        REPORTS_DIR,
        SQL_DIR,
        STAGING_SQL_DIR,
        MARTS_SQL_DIR
    ]
    for d in expected_dirs:
        assert d.exists(), f"Directory {d} does not exist"
