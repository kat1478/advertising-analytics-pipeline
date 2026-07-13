CREATE OR REPLACE TABLE stg_campaigns AS
SELECT DISTINCT
    CAST(SUBSTR(campaign_id, 2) AS INTEGER) AS campaign_id,
    CAST(campaign_name AS VARCHAR) AS campaign_name,
    CAST(channel AS VARCHAR) AS channel,
    CAST(start_date AS DATE) AS start_date,
    CAST(end_date AS DATE) AS end_date,
    CAST(budget AS DOUBLE) AS budget,
    CAST(target_segment AS VARCHAR) AS target_segment
FROM raw_campaigns;
