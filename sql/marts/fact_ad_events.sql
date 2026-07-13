CREATE OR REPLACE TABLE fact_ad_events AS
WITH daily_impressions AS (
    SELECT event_date, campaign_id, product_id, COUNT(*) as impressions
    FROM stg_impressions
    GROUP BY 1, 2, 3
),
daily_clicks AS (
    SELECT i.event_date, c.campaign_id, c.product_id, COUNT(*) as clicks
    FROM stg_clicks c
    JOIN stg_impressions i ON c.impression_id = i.impression_id
    GROUP BY 1, 2, 3
),
daily_conversions AS (
    SELECT i.event_date, cv.campaign_id, cv.product_id, COUNT(*) as conversions, SUM(cv.revenue) as revenue
    FROM stg_conversions cv
    JOIN stg_clicks c ON cv.click_id = c.click_id
    JOIN stg_impressions i ON c.impression_id = i.impression_id
    GROUP BY 1, 2, 3
),
campaign_daily_totals AS (
    SELECT event_date, campaign_id, SUM(impressions) as total_impressions
    FROM daily_impressions
    GROUP BY 1, 2
),
base AS (
    SELECT DISTINCT event_date, campaign_id, product_id FROM daily_impressions
    UNION
    SELECT DISTINCT event_date, campaign_id, product_id FROM daily_clicks
    UNION
    SELECT DISTINCT event_date, campaign_id, product_id FROM daily_conversions
)
SELECT 
    b.event_date,
    b.campaign_id,
    b.product_id,
    COALESCE(i.impressions, 0) AS impressions,
    COALESCE(c.clicks, 0) AS clicks,
    COALESCE(cv.conversions, 0) AS conversions,
    COALESCE(cv.revenue, 0.0) AS revenue,
    COALESCE(
        co.cost * (CAST(i.impressions AS DOUBLE) / NULLIF(cdt.total_impressions, 0)), 
        0.0
    ) AS cost
FROM base b
LEFT JOIN daily_impressions i ON b.event_date = i.event_date AND b.campaign_id = i.campaign_id AND b.product_id = i.product_id
LEFT JOIN daily_clicks c ON b.event_date = c.event_date AND b.campaign_id = c.campaign_id AND b.product_id = c.product_id
LEFT JOIN daily_conversions cv ON b.event_date = cv.event_date AND b.campaign_id = cv.campaign_id AND b.product_id = cv.product_id
LEFT JOIN stg_costs co ON b.event_date = co.event_date AND b.campaign_id = co.campaign_id
LEFT JOIN campaign_daily_totals cdt ON b.event_date = cdt.event_date AND b.campaign_id = cdt.campaign_id;
