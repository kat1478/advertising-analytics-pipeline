import logging
from src.paths import PROJECT_ROOT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting pipeline scaffold...")
    logger.info(f"Project root is: {PROJECT_ROOT}")
    logger.info("Scaffold is ready.")

if __name__ == "__main__":
    main()
