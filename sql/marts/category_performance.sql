CREATE OR REPLACE TABLE category_performance AS
SELECT 
    p.category,
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
FROM fact_campaign_product_daily f
LEFT JOIN dim_products p ON f.product_id = p.product_id
GROUP BY 1;
