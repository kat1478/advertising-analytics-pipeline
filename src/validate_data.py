import duckdb
import logging
from src.paths import DATABASE_PATH

logger = logging.getLogger(__name__)

def run_validations(db_path=DATABASE_PATH):
    conn = duckdb.connect(str(db_path))
    results = {'passed': [], 'failed': []}

    def check(condition, message):
        if condition:
            results['passed'].append(message)
        else:
            results['failed'].append(message)

    try:
        tables_res = conn.execute("SHOW TABLES").fetchall()
        tables = [t[0] for t in tables_res]
        
        required_tables = [
            'raw_campaigns', 'raw_products', 'raw_impressions', 
            'raw_clicks', 'raw_costs', 'raw_conversions'
        ]
        
        for t in required_tables:
            check(t in tables, f"Table {t} exists")
            if t not in tables:
                return results # stop further checks if missing tables

        # Primary Keys Not Null
        check(conn.execute("SELECT COUNT(*) FROM raw_campaigns WHERE campaign_id IS NULL").fetchone()[0] == 0, "PK raw_campaigns.campaign_id not null")
        check(conn.execute("SELECT COUNT(*) FROM raw_products WHERE product_id IS NULL").fetchone()[0] == 0, "PK raw_products.product_id not null")
        check(conn.execute("SELECT COUNT(*) FROM raw_impressions WHERE impression_id IS NULL").fetchone()[0] == 0, "PK raw_impressions.impression_id not null")
        check(conn.execute("SELECT COUNT(*) FROM raw_clicks WHERE click_id IS NULL").fetchone()[0] == 0, "PK raw_clicks.click_id not null")
        check(conn.execute("SELECT COUNT(*) FROM raw_conversions WHERE conversion_id IS NULL").fetchone()[0] == 0, "PK raw_conversions.conversion_id not null")

        # Primary Keys Unique
        check(conn.execute("SELECT COUNT(campaign_id) - COUNT(DISTINCT campaign_id) FROM raw_campaigns").fetchone()[0] == 0, "PK raw_campaigns.campaign_id unique")
        check(conn.execute("SELECT COUNT(product_id) - COUNT(DISTINCT product_id) FROM raw_products").fetchone()[0] == 0, "PK raw_products.product_id unique")
        check(conn.execute("SELECT COUNT(impression_id) - COUNT(DISTINCT impression_id) FROM raw_impressions").fetchone()[0] == 0, "PK raw_impressions.impression_id unique")
        check(conn.execute("SELECT COUNT(click_id) - COUNT(DISTINCT click_id) FROM raw_clicks").fetchone()[0] == 0, "PK raw_clicks.click_id unique")
        check(conn.execute("SELECT COUNT(conversion_id) - COUNT(DISTINCT conversion_id) FROM raw_conversions").fetchone()[0] == 0, "PK raw_conversions.conversion_id unique")

        # Foreign Key Relationships
        check(conn.execute("SELECT COUNT(*) FROM raw_impressions WHERE campaign_id NOT IN (SELECT campaign_id FROM raw_campaigns)").fetchone()[0] == 0, "FK raw_impressions -> raw_campaigns")
        check(conn.execute("SELECT COUNT(*) FROM raw_impressions WHERE product_id NOT IN (SELECT product_id FROM raw_products)").fetchone()[0] == 0, "FK raw_impressions -> raw_products")
        check(conn.execute("SELECT COUNT(*) FROM raw_clicks WHERE impression_id NOT IN (SELECT impression_id FROM raw_impressions)").fetchone()[0] == 0, "FK raw_clicks -> raw_impressions")
        check(conn.execute("SELECT COUNT(*) FROM raw_conversions WHERE click_id NOT IN (SELECT click_id FROM raw_clicks)").fetchone()[0] == 0, "FK raw_conversions -> raw_clicks")

        # Numeric Sanity Checks
        check(conn.execute("SELECT COUNT(*) FROM raw_campaigns WHERE budget < 0").fetchone()[0] == 0, "Numeric raw_campaigns.budget >= 0")
        check(conn.execute("SELECT COUNT(*) FROM raw_products WHERE price < 0").fetchone()[0] == 0, "Numeric raw_products.price >= 0")
        check(conn.execute("SELECT COUNT(*) FROM raw_costs WHERE cost < 0").fetchone()[0] == 0, "Numeric raw_costs.cost >= 0")
        check(conn.execute("SELECT COUNT(*) FROM raw_conversions WHERE revenue < 0").fetchone()[0] == 0, "Numeric raw_conversions.revenue >= 0")

        # Required Timestamp Fields Not Null
        check(conn.execute("SELECT COUNT(*) FROM raw_impressions WHERE event_timestamp IS NULL").fetchone()[0] == 0, "Timestamp raw_impressions.event_timestamp not null")
        check(conn.execute("SELECT COUNT(*) FROM raw_clicks WHERE event_timestamp IS NULL").fetchone()[0] == 0, "Timestamp raw_clicks.event_timestamp not null")
        check(conn.execute("SELECT COUNT(*) FROM raw_costs WHERE event_date IS NULL").fetchone()[0] == 0, "Date raw_costs.event_date not null")
        check(conn.execute("SELECT COUNT(*) FROM raw_conversions WHERE event_timestamp IS NULL").fetchone()[0] == 0, "Timestamp raw_conversions.event_timestamp not null")

    finally:
        conn.close()

    for msg in results['passed']:
        logger.info(f"[PASS] {msg}")
    for msg in results['failed']:
        logger.error(f"[FAIL] {msg}")

    return results

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Starting Raw Data Validation...")
    results = run_validations()
    if results['failed']:
        logger.error("Validation failed.")
        exit(1)
    else:
        logger.info("Validation passed successfully.")

if __name__ == "__main__":
    main()
