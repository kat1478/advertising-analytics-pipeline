# Advertising Analytics Pipeline Reporting

The pipeline generates automated, business-readable Markdown reports from the analytical mart tables.

## Generating the Report

Run after the full pipeline (staging + marts) has been executed:

```bash
python -m src.generate_report
python -m src.analytics_assistant
```

Output files:
- `reports/campaign_report.md` — quantitative performance report
- `reports/analytics_insights.md` — classified business recommendations

## Report Contents

**`reports/campaign_report.md`**:
- **Pipeline Context** — deterministic metadata (seed, reporting period, currency)
- **Executive Summary** — total impressions, clicks, conversions, spend, and aggregate KPIs
- **Top Campaigns** — top 5 by ROAS, Revenue, and Conversion Rate
- **Underperforming Campaigns** — campaigns flagged by classification rules (see below)
- **Category Performance** — aggregated metrics by product category
- **Interpretation Notes** — metric definitions with PLN context

**`reports/analytics_insights.md`**:
- One-line classification per campaign (Critical / Warning / Monitor / Opportunity)
- Category-level opportunities and risks
- Threshold reference table

## Classification Rules

Both the performance report and the analytics assistant apply the following classification rules.
Thresholds are defined centrally in `src/config.py`.

### Campaign-level classifications

| Classification | Condition |
|---|---|
| **Critical** | Cost above dataset median **AND** ROAS < `LOW_ROAS_THRESHOLD` (1.5) |
| **Warning** | CPC > `HIGH_CPC_THRESHOLD` (5 zł) **AND** CVR < `LOW_CVR_THRESHOLD` (5%) |
| **Monitor** | Strong ROAS (>= 3.0) but CVR < 5%, or high CTR but low CVR |
| **Opportunity** | ROAS >= `HIGH_ROAS_THRESHOLD` (3.0); exceptional if ROAS >= 5.0 |

Each campaign receives **at most one classification** — the highest-severity signal wins.
This prevents contradictory recommendations for the same campaign.

### Report underperforming sections

| Section | Rule |
|---|---|
| High CTR / Low Conversion Rate | CTR above dataset mean **AND** CVR < `LOW_CVR_THRESHOLD` (5%) |
| High Cost / Low ROAS | Cost above dataset median **AND** ROAS < `LOW_ROAS_THRESHOLD` (1.5) |
| Highest Cost per Conversion | Top 5 campaigns where conversions > 0, sorted by descending CPA |

### Category-level flags

| Flag | Condition |
|---|---|
| Opportunity | Category ROAS >= `HIGH_ROAS_THRESHOLD` (3.0) |
| Risk | Category ROAS < `LOW_ROAS_THRESHOLD` (1.5) |

### Threshold rationale

- **Absolute floors** (ROAS, CPC, CVR thresholds) prevent distortion when the dataset contains extreme outliers.
- **Dataset-relative context** (median cost) ensures high/low spend comparisons adapt to the actual portfolio scale.
- A combination of both approaches is more robust than purely relative multipliers for a demonstration dataset with synthetic economics.

## Analytical Context

All metrics are fetched from the `daily_campaign_performance` and `category_performance` DuckDB marts. 
Currency is **PLN (zł)** throughout.  
No runtime timestamps are embedded in committed sample outputs; deterministic metadata (seed, period) is used instead.
