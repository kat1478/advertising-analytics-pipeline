# Advertising Analytics Performance Report

This report is generated from synthetic advertising data to demonstrate pipeline outputs.

## Pipeline Context

- **Source Marts:** `daily_campaign_performance`, `category_performance`
- **Generated At:** 2026-07-17 16:20:46
- **Note:** Metrics are calculated in SQL marts and aggregated here for reporting.

## Executive Summary

- **Total Impressions:** 10,000
- **Total Clicks:** 461
- **Total Conversions:** 68
- **Total Cost:** $310.34
- **Total Revenue:** $77,770.02
- **Overall CTR:** 4.61%
- **Overall CPC:** $0.67
- **Overall Conversion Rate:** 14.75%
- **Overall ROAS:** 250.60
- **Overall Cost per Conversion:** $4.56

## Top Campaigns

### Top 5 by ROAS

| campaign_name | roas | revenue |
|---------------|------|---------|
| Campaign_2 | 489.63 | 6,355.45 |
| Campaign_11 | 477.82 | 7,884.05 |
| Campaign_6 | 428.81 | 5,926.11 |
| Campaign_4 | 426.09 | 7,098.66 |
| Campaign_19 | 385.22 | 6,178.87 |

### Top 5 by Revenue

| campaign_name | revenue | roas |
|---------------|---------|------|
| Campaign_11 | 7,884.05 | 477.82 |
| Campaign_4 | 7,098.66 | 426.09 |
| Campaign_2 | 6,355.45 | 489.63 |
| Campaign_19 | 6,178.87 | 385.22 |
| Campaign_6 | 5,926.11 | 428.81 |

### Top 5 by Conversion Rate

| campaign_name | conversion_rate | conversions |
|---------------|-----------------|-------------|
| Campaign_2 | 27.27% | 6 |
| Campaign_19 | 22.73% | 5 |
| Campaign_8 | 22.22% | 6 |
| Campaign_4 | 20.69% | 6 |
| Campaign_5 | 20.00% | 4 |

## Underperforming Campaigns

### High CTR, Low Conversion Rate

| campaign_name | ctr | conversion_rate | cost |
|---------------|-----|-----------------|------|
| Campaign_3 | 5.59% | 10.34% | 17.44 |
| Campaign_17 | 4.63% | 4.35% | 16.40 |
| Campaign_1 | 5.26% | 12.00% | 14.36 |
| Campaign_6 | 6.64% | 9.68% | 13.82 |

### High Cost, Low ROAS

| campaign_name | cost | roas | revenue |
|---------------|------|------|---------|
| Campaign_5 | 16.88 | 192.31 | 3,246.12 |
| Campaign_7 | 16.81 | 79.78 | 1,341.18 |
| Campaign_17 | 16.40 | 114.39 | 1,876.02 |
| Campaign_15 | 16.15 | 165.66 | 2,675.45 |

### Highest Cost per Conversion

| campaign_name | cost_per_conversion | conversions | cost |
|---------------|---------------------|-------------|------|
| Campaign_7 | 16.81 | 1 | 16.81 |
| Campaign_17 | 16.40 | 1 | 16.40 |
| Campaign_12 | 14.35 | 1 | 14.35 |
| Campaign_13 | 13.90 | 1 | 13.90 |
| Campaign_15 | 8.07 | 2 | 16.15 |

## Category Performance

### Top Categories by Revenue

| category | revenue | roas |
|----------|---------|------|
| Electronics | 27,111.76 | 312.66 |
| Home | 24,581.94 | 392.87 |
| Toys | 10,300.73 | 199.88 |
| Sports | 8,373.93 | 159.20 |
| Clothing | 7,401.66 | 130.04 |

### Top Categories by ROAS

| category | roas | revenue |
|----------|------|---------|
| Home | 392.87 | 24,581.94 |
| Electronics | 312.66 | 27,111.76 |
| Toys | 199.88 | 10,300.73 |
| Sports | 159.20 | 8,373.93 |
| Clothing | 130.04 | 7,401.66 |

### Categories with Weakest Conversion Rate

| category | conversion_rate | conversions |
|----------|-----------------|-------------|
| Sports | 8.97% | 7 |
| Clothing | 12.33% | 9 |
| Toys | 14.67% | 11 |
| Electronics | 14.89% | 21 |
| Home | 21.28% | 20 |

## Data Quality Notes

This report relies on data that has passed automated upstream validation and metric quality tests. Key assumptions enforced during the pipeline execution include:
- All metrics are strictly non-negative.
- Safe division is employed to prevent division-by-zero errors.
- An impression-based attribution model is used to ensure daily funnel consistency (clicks <= impressions, conversions <= clicks).

## Interpretation Notes

- **CTR (Click-Through Rate):** The percentage of impressions that led to a click. A high CTR indicates the ad is engaging.
- **CPC (Cost Per Click):** How much you pay on average for each ad click.
- **Conversion Rate:** The percentage of clicks that resulted in a purchase. A high conversion rate indicates the product or landing page is effective.
- **ROAS (Return on Ad Spend):** The revenue generated for every dollar spent on advertising. A ROAS of 2.0 means $2 in revenue for every $1 spent.
- **Cost per Conversion:** The average cost to acquire one conversion or purchase.