# Advertising Analytics Performance Report

This report is generated from synthetic advertising data to demonstrate pipeline outputs.

## Pipeline Context

- **Source Marts:** `daily_campaign_performance`, `category_performance`
- **Dataset Seed:** 42
- **Reporting Period:** 2023-06-01 – 2023-06-30
- **Currency:** PLN (zł)
- **Attribution:** Impression-based cohort (event_date from originating impression)

## Executive Summary

- **Total Impressions:** 10,000
- **Total Clicks:** 461
- **Total Conversions:** 99
- **Total Cost:** 5,118.03 zł
- **Total Revenue:** 40,455.01 zł
- **Overall CTR:** 4.61%
- **Overall CPC:** 11.10 zł
- **Overall Conversion Rate:** 21.48%
- **Overall ROAS:** 7.90
- **Overall Cost per Conversion:** 51.70 zł

## Top Campaigns

### Top 5 by ROAS

| campaign_name | roas | revenue |
|---------------|------|---------|
| Campaign_2 | 22.95 | 2,021.87 zł |
| Campaign_10 | 21.88 | 2,152.41 zł |
| Campaign_11 | 16.27 | 3,527.37 zł |
| Campaign_6 | 16.16 | 2,989.67 zł |
| Campaign_20 | 14.33 | 2,989.94 zł |

### Top 5 by Revenue

| campaign_name | revenue | roas |
|---------------|---------|------|
| Campaign_8 | 4,002.91 zł | 7.73 |
| Campaign_4 | 3,875.72 zł | 7.08 |
| Campaign_11 | 3,527.37 zł | 16.27 |
| Campaign_20 | 2,989.94 zł | 14.33 |
| Campaign_6 | 2,989.67 zł | 16.16 |

### Top 5 by Conversion Rate

| campaign_name | conversion_rate | conversions |
|---------------|-----------------|-------------|
| Campaign_8 | 37.04% | 10 |
| Campaign_2 | 31.82% | 7 |
| Campaign_4 | 31.03% | 9 |
| Campaign_10 | 28.57% | 6 |
| Campaign_18 | 28.57% | 8 |

## Underperforming Campaigns

*Classification rules: High CTR/Low CVR — CTR above dataset mean and CVR below 5%. High Cost/Low ROAS — cost above dataset median and ROAS below 1.5. See [docs/REPORTING.md](../docs/REPORTING.md) for details.*

### High CTR, Low Conversion Rate

No data available.

### High Cost, Low ROAS

| campaign_name | cost | roas | revenue |
|---------------|------|------|---------|
| Campaign_12 | 477.12 zł | 0.72 | 343.49 zł |

### Highest Cost per Conversion

| campaign_name | cost_per_conversion | conversions | cost |
|---------------|---------------------|-------------|------|
| Campaign_12 | 477.12 zł | 1 | 477.12 zł |
| Campaign_15 | 176.44 zł | 3 | 529.33 zł |
| Campaign_1 | 95.57 zł | 5 | 477.86 zł |
| Campaign_7 | 73.25 zł | 3 | 219.74 zł |
| Campaign_16 | 64.54 zł | 3 | 193.63 zł |

## Category Performance

### Top Categories by Revenue

| category | revenue | roas |
|----------|---------|------|
| Electronics | 11,379.67 zł | 8.02 |
| Home | 11,264.15 zł | 11.00 |
| Sports | 7,129.36 zł | 8.17 |
| Toys | 5,364.03 zł | 6.24 |
| Clothing | 5,317.80 zł | 5.64 |

### Top Categories by ROAS

| category | roas | revenue |
|----------|------|---------|
| Home | 11.00 | 11,264.15 zł |
| Sports | 8.17 | 7,129.36 zł |
| Electronics | 8.02 | 11,379.67 zł |
| Toys | 6.24 | 5,364.03 zł |
| Clothing | 5.64 | 5,317.80 zł |

### Categories with Weakest Conversion Rate

| category | conversion_rate | conversions |
|----------|-----------------|-------------|
| Sports | 19.23% | 15 |
| Clothing | 20.55% | 15 |
| Electronics | 20.57% | 29 |
| Toys | 21.33% | 16 |
| Home | 25.53% | 24 |

## Data Quality Notes

This report relies on data that has passed automated upstream validation and metric quality tests. Key assumptions enforced during pipeline execution:
- All metrics are strictly non-negative.
- Safe division (NULLIF) prevents division-by-zero errors.
- An impression-based attribution model is used to ensure daily funnel consistency (clicks <= impressions, conversions <= clicks).

## Interpretation Notes

- **CTR (Click-Through Rate):** The percentage of impressions that led to a click. A high CTR indicates the ad is engaging.
- **CPC (Cost Per Click):** How much is paid on average for each ad click (PLN).
- **Conversion Rate:** The percentage of clicks that resulted in a purchase. A high rate indicates the product or landing page is effective.
- **ROAS (Return on Ad Spend):** Revenue generated per PLN spent. ROAS < 1.5 is considered weak; above 3.0 is strong.
- **Cost per Conversion:** The average cost to acquire one conversion (PLN).