CREATE OR REPLACE TABLE stg_impressions AS
SELECT DISTINCT
    CAST(SUBSTR(impression_id, 2) AS INTEGER) AS impression_id,
    CAST(SUBSTR(campaign_id, 2) AS INTEGER) AS campaign_id,
    CAST(SUBSTR(product_id, 2) AS INTEGER) AS product_id,
    CAST(user_segment AS VARCHAR) AS user_segment,
    CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
    CAST(event_timestamp AS DATE) AS event_date
FROM raw_impressions;
