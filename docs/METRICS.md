# Analytical Metrics and Data Quality

This document describes the core metrics and data quality checks implemented in the Advertising Analytics Data Pipeline.

## Currency

All monetary metrics are expressed in **PLN (Polish Złoty, zł)**.

## Core Metrics Definitions

The following advertising metrics are calculated across the analytical marts (`daily_campaign_performance`, `category_performance`):

- **CTR (Click-Through Rate)**: `clicks / impressions`
  - *Definition*: The percentage of impressions that resulted in a click.
  - *Constraint*: Must be between 0 and 1.

- **CPC (Cost Per Click)**: `cost / clicks`
  - *Definition*: The average cost (PLN) incurred for each ad click.
  - *Constraint*: Must be non-negative.

- **Conversion Rate**: `conversions / clicks`
  - *Definition*: The percentage of clicks that resulted in a conversion.
  - *Constraint*: Must be between 0 and 1.

- **ROAS (Return on Ad Spend)**: `revenue / cost`
  - *Definition*: Revenue generated per PLN spent on advertising.
  - *Constraint*: Must be non-negative.
  - *Interpretation*:
    | ROAS | Interpretation |
    |------|----------------|
    | < 1.5 | Weak — campaign does not cover its cost effectively |
    | 1.5 – 3.0 | Moderate — acceptable but room for improvement |
    | 3.0 – 5.0 | Strong — good return |
    | > 5.0 | Exceptional — scale candidate |

- **Cost per Conversion**: `cost / conversions`
  - *Definition*: The average cost (PLN) required to acquire one conversion.
  - *Constraint*: Must be non-negative.

### Safe Division
All ratio metrics are calculated using safe division (`NULLIF(denominator, 0)`) to prevent division by zero errors. If the denominator is zero, the metric evaluates to `NULL`.

## Fact Table Grain

The primary fact table is **`fact_campaign_product_daily`** (located in `sql/marts/fact_campaign_product_daily.sql`).

Its grain is: **`event_date × campaign_id × product_id`**

Each row represents the aggregated advertising activity for one campaign, one product, on one calendar day.  This is not an individual-event table.

## Cost Allocation Strategy

In the raw data, operational cost is provided at the **campaign × daily** grain. The fact table is maintained at a lower grain: **campaign × product × daily**.

To distribute the campaign cost accurately down to individual products within that campaign on a given day, a proportional allocation strategy based on impressions is used:

```
Product Cost = Total Campaign Cost × (Product Impressions / Total Campaign Impressions)
```

This ensures that products receiving more impressions carry a proportional amount of the daily campaign budget.  Automated tests verify that the sum of allocated costs per campaign-day matches the original source cost (within a floating-point tolerance of 0.01 PLN).

## Data Quality Assumptions Tested

Data quality constraints are enforced via automated pytest pipelines (`tests/test_metrics_quality.py`). These checks include:

1. **Primary Key Uniqueness**: No duplicate rows across business keys (e.g., `event_date` + `campaign_id`).
2. **Logical Funnel Constraints**:
   - `clicks <= impressions`
   - `conversions <= clicks`
3. **Non-Negativity**: Impressions, clicks, conversions, cost, and revenue are strictly >= 0.
4. **Metric Bounds**: Ratio metrics (CTR, Conversion Rate) fall within the [0, 1] interval.
5. **Cost Reconciliation**: Allocated costs in `fact_campaign_product_daily` match source costs in `stg_costs`.
