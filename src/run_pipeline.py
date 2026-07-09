import logging
from src.paths import PROJECT_ROOT
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.validate_data import run_validations
from src.run_sql import execute_sql_files

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting pipeline execution...")
    
    logger.info("1. Generating synthetic data...")
    generate_data_main()
    
    logger.info("2. Loading raw data...")
    load_raw_data()
    
    logger.info("3. Validating raw data...")
    val_results = run_validations()
    if val_results['failed']:
        logger.error("Pipeline aborted due to raw data validation failure.")
        exit(1)
        
    logger.info("4. Running staging SQL...")
    execute_sql_files()
    
    logger.info("Pipeline executed successfully (up to staging).")

if __name__ == "__main__":
    main()
