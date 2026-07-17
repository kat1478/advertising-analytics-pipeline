# Advertising Analytics Pipeline Reporting

The pipeline generates an automated business-ready markdown report to quickly assess advertising performance.

## Generating the Report

Run the following command after fully processing the analytical marts:
```bash
python -m src.generate_report
```

This will create a `reports/campaign_report.md` file.

## Report Contents

The generated report contains:
- **Executive Summary:** High-level overview of total impressions, clicks, conversions, spend, and aggregate metrics.
- **Top Campaigns:** Identifies the top 5 campaigns by Return on Ad Spend (ROAS), Revenue, and Conversion Rate.
- **Underperforming Campaigns:** Highlights campaigns that are struggling (e.g. high CTR but low conversion rate, high cost but low ROAS).
- **Category Performance:** Aggregates performance metrics across product categories.
- **Interpretation & Data Quality:** Contextual notes regarding the underlying assumptions (e.g., non-negative constraints, funnel cascade conditions, impression-based attribution cohorting) and straightforward business definitions of acronyms.

## Analytical Context

All metrics are fetched natively from the `daily_campaign_performance` and `category_performance` DuckDB marts. The script aggregates and cleanly formats these numerical KPIs into a markdown structure tailored for non-technical stakeholders.
