# Analytical Metrics and Data Quality

This document describes the core metrics and data quality checks implemented in the Advertising Analytics Data Pipeline.

## Core Metrics Definitions

The following advertising metrics are calculated across the analytical marts (`daily_campaign_performance`, `category_performance`):

- **CTR (Click-Through Rate)**: `clicks / impressions`
  - *Definition*: The percentage of impressions that resulted in a click.
  - *Constraint*: Must be between 0 and 1.
- **CPC (Cost Per Click)**: `cost / clicks`
  - *Definition*: The average cost incurred for each ad click.
  - *Constraint*: Must be non-negative.
- **Conversion Rate**: `conversions / clicks`
  - *Definition*: The percentage of clicks that resulted in a conversion.
  - *Constraint*: Must be between 0 and 1.
- **ROAS (Return on Ad Spend)**: `revenue / cost`
  - *Definition*: The revenue generated for every dollar spent on advertising.
  - *Constraint*: Must be non-negative.
- **Cost per Conversion**: `cost / conversions`
  - *Definition*: The average cost required to acquire one conversion.
  - *Constraint*: Must be non-negative.

### Safe Division
All ratio metrics are calculated using safe division (e.g., `NULLIF(clicks, 0)`) to prevent division by zero errors. If the denominator is zero, the metric evaluates to `NULL`.

## Cost Allocation Strategy

In the raw data, operational cost is provided at the **campaign** and **daily** grain. However, the event fact table (`fact_ad_events`) is maintained at a lower grain: **campaign**, **product**, and **daily**. 

To distribute the high-level campaign cost accurately down to individual products within that campaign on a given day, we employ a proportional cost allocation strategy based on impressions:
- `Product Cost = Total Campaign Cost * (Product Impressions / Total Campaign Impressions)`

This ensures that products receiving more impressions carry a proportional amount of the daily campaign budget. Our quality tests verify that the sum of allocated costs per campaign-day accurately matches the original source cost.

## Data Quality Assumptions Tested

We enforce data quality constraints via automated test pipelines (`tests/test_metrics_quality.py`). These checks include:
1. **Primary Key Uniqueness**: No duplicate rows exist across business keys (e.g., `event_date` + `campaign_id`).
2. **Logical Funnel Constraints**: 
   - `clicks <= impressions`
   - `conversions <= clicks`
3. **Non-Negativity**: Impressions, clicks, conversions, cost, and revenue are strictly >= 0.
4. **Metric Bounds**: Ratio metrics (CTR, Conversion Rate) fall securely within the [0, 1] interval.
