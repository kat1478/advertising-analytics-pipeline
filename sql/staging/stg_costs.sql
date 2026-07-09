CREATE OR REPLACE TABLE stg_costs AS
SELECT DISTINCT
    CAST(SUBSTR(campaign_id, 2) AS INTEGER) AS campaign_id,
    CAST(event_date AS DATE) AS event_date,
    CAST(cost AS DOUBLE) AS cost
FROM raw_costs;
