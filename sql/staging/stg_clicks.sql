CREATE OR REPLACE TABLE stg_clicks AS
SELECT DISTINCT
    CAST(SUBSTR(click_id, 3) AS INTEGER) AS click_id,
    CAST(SUBSTR(impression_id, 2) AS INTEGER) AS impression_id,
    CAST(SUBSTR(campaign_id, 2) AS INTEGER) AS campaign_id,
    CAST(SUBSTR(product_id, 2) AS INTEGER) AS product_id,
    CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
    CAST(event_timestamp AS DATE) AS event_date
FROM raw_clicks;
