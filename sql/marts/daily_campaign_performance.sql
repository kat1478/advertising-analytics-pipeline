CREATE OR REPLACE TABLE daily_campaign_performance AS
SELECT 
    f.event_date,
    f.campaign_id,
    c.campaign_name,
    c.channel,
    SUM(f.impressions) AS impressions,
    SUM(f.clicks) AS clicks,
    SUM(f.conversions) AS conversions,
    SUM(f.cost) AS cost,
    SUM(f.revenue) AS revenue,
    SUM(f.clicks) / NULLIF(SUM(f.impressions), 0) AS ctr,
    SUM(f.cost) / NULLIF(SUM(f.clicks), 0) AS cpc,
    SUM(f.conversions) / NULLIF(SUM(f.clicks), 0) AS conversion_rate,
    SUM(f.revenue) / NULLIF(SUM(f.cost), 0) AS roas,
    SUM(f.cost) / NULLIF(SUM(f.conversions), 0) AS cost_per_conversion
FROM fact_ad_events f
LEFT JOIN dim_campaigns c ON f.campaign_id = c.campaign_id
GROUP BY 1, 2, 3, 4;
