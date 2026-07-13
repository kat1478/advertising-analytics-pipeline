CREATE OR REPLACE TABLE dim_campaigns AS
SELECT
    campaign_id,
    campaign_name,
    channel,
    start_date,
    end_date,
    budget,
    target_segment
FROM stg_campaigns;
