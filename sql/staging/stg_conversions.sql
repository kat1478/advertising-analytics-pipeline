CREATE OR REPLACE TABLE stg_conversions AS
SELECT DISTINCT
    CAST(SUBSTR(conversion_id, 3) AS INTEGER) AS conversion_id,
    CAST(SUBSTR(click_id, 3) AS INTEGER) AS click_id,
    CAST(SUBSTR(campaign_id, 2) AS INTEGER) AS campaign_id,
    CAST(SUBSTR(product_id, 2) AS INTEGER) AS product_id,
    CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
    CAST(event_timestamp AS DATE) AS event_date,
    CAST(revenue AS DOUBLE) AS revenue
FROM raw_conversions;
