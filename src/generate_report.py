import duckdb
import pandas as pd
from pathlib import Path
from src.paths import DATABASE_PATH, PROJECT_ROOT
from src.config import (
    CURRENCY_SYMBOL,
    CURRENCY_CODE,
    DATASET_SEED,
    REPORTING_PERIOD,
    LOW_ROAS_THRESHOLD,
    HIGH_ROAS_THRESHOLD,
    LOW_CVR_THRESHOLD,
)
import logging

logger = logging.getLogger(__name__)


def fmt_currency(value):
    """Format a numeric value as a currency string using the project currency."""
    if pd.isnull(value):
        return "N/A"
    return f"{value:,.2f} {CURRENCY_SYMBOL}"


def fmt_pct(value):
    """Format a numeric value as a percentage string."""
    if pd.isnull(value):
        return "N/A"
    return f"{value:.2%}"


def to_markdown_table(df):
    if df.empty:
        return "No data available.\n"
    formatted_df = df.copy()
    for col in formatted_df.columns:
        if 'rate' in col.lower() or col.lower() == 'ctr':
            formatted_df[col] = formatted_df[col].map(fmt_pct)
        elif col.lower() in ['cost', 'revenue', 'cost_per_conversion', 'cpc']:
            formatted_df[col] = formatted_df[col].map(fmt_currency)
        elif col.lower() == 'roas':
            formatted_df[col] = formatted_df[col].map(
                lambda x: f"{x:.2f}" if pd.notnull(x) else "N/A"
            )
        else:
            formatted_df[col] = formatted_df[col].map(
                lambda x: f"{x:,.0f}" if pd.notnull(x) and isinstance(x, (int, float)) else str(x)
            )

    header = "| " + " | ".join(formatted_df.columns) + " |"
    separator = "|-" + "-|-".join(["-" * len(col) for col in formatted_df.columns]) + "-|"
    rows = []
    for _, row in formatted_df.iterrows():
        rows.append("| " + " | ".join(str(x) for x in row.values) + " |")
    return "\n".join([header, separator] + rows) + "\n"


def generate_report(db_path=DATABASE_PATH, report_dir=PROJECT_ROOT / "reports"):
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "campaign_report.md"

    conn = duckdb.connect(str(db_path))

    exec_summary = conn.execute("""
        SELECT 
            SUM(impressions) as total_impressions,
            SUM(clicks) as total_clicks,
            SUM(conversions) as total_conversions,
            SUM(cost) as total_cost,
            SUM(revenue) as total_revenue,
            SUM(clicks) / NULLIF(SUM(impressions), 0) as overall_ctr,
            SUM(cost) / NULLIF(SUM(clicks), 0) as overall_cpc,
            SUM(conversions) / NULLIF(SUM(clicks), 0) as overall_conversion_rate,
            SUM(revenue) / NULLIF(SUM(cost), 0) as overall_roas,
            SUM(cost) / NULLIF(SUM(conversions), 0) as overall_cost_per_conversion
        FROM daily_campaign_performance
    """).df().iloc[0]

    camp_agg = conn.execute("""
        SELECT 
            campaign_name,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(conversions) as conversions,
            SUM(cost) as cost,
            SUM(revenue) as revenue,
            SUM(clicks) / NULLIF(SUM(impressions), 0) as ctr,
            SUM(conversions) / NULLIF(SUM(clicks), 0) as conversion_rate,
            SUM(revenue) / NULLIF(SUM(cost), 0) as roas,
            SUM(cost) / NULLIF(SUM(conversions), 0) as cost_per_conversion
        FROM daily_campaign_performance
        GROUP BY campaign_name
        ORDER BY campaign_name
    """).df()

    top_roas = camp_agg.sort_values('roas', ascending=False).head(5)
    top_rev = camp_agg.sort_values('revenue', ascending=False).head(5)
    top_cvr = camp_agg.sort_values('conversion_rate', ascending=False).head(5)

    avg_ctr = exec_summary['overall_ctr']
    avg_cvr = exec_summary['overall_conversion_rate']
    avg_roas = exec_summary['overall_roas']

    # Classification rules (documented in docs/REPORTING.md):
    # - High CTR / Low CVR: CTR above dataset average AND CVR below LOW_CVR_THRESHOLD
    # - High Cost / Low ROAS: cost above dataset median AND ROAS below LOW_ROAS_THRESHOLD
    # - Highest CPA: top 5 by cost_per_conversion (where conversions exist)
    high_ctr_low_cvr = camp_agg[
        (camp_agg['ctr'] > avg_ctr) & (camp_agg['conversion_rate'] < LOW_CVR_THRESHOLD)
    ].sort_values('cost', ascending=False).head(5)

    high_cost_low_roas = camp_agg[
        (camp_agg['cost'] > camp_agg['cost'].median()) & (camp_agg['roas'] < LOW_ROAS_THRESHOLD)
    ].sort_values('cost', ascending=False).head(5)

    high_cpa = camp_agg[camp_agg['conversions'] > 0].sort_values(
        'cost_per_conversion', ascending=False
    ).head(5)

    cat_perf = conn.execute("""
        SELECT 
            category,
            impressions,
            clicks,
            conversions,
            cost,
            revenue,
            ctr,
            conversion_rate,
            roas,
            cost_per_conversion
        FROM category_performance
        ORDER BY revenue DESC
    """).df()

    conn.close()

    top_cat_rev = cat_perf.sort_values('revenue', ascending=False).head(5)
    top_cat_roas = cat_perf.sort_values('roas', ascending=False).head(5)
    weak_cat_cvr = cat_perf.sort_values('conversion_rate', ascending=True).head(5)

    md = []
    md.append("# Advertising Analytics Performance Report\n")
    md.append("This report is generated from synthetic advertising data to demonstrate pipeline outputs.\n")

    md.append("## Pipeline Context\n")
    md.append(f"- **Source Marts:** `daily_campaign_performance`, `category_performance`")
    md.append(f"- **Dataset Seed:** {DATASET_SEED}")
    md.append(f"- **Reporting Period:** {REPORTING_PERIOD}")
    md.append(f"- **Currency:** {CURRENCY_CODE} ({CURRENCY_SYMBOL})")
    md.append("- **Attribution:** Impression-based cohort (event_date from originating impression)\n")

    md.append("## Executive Summary\n")
    md.append(f"- **Total Impressions:** {exec_summary['total_impressions']:,.0f}")
    md.append(f"- **Total Clicks:** {exec_summary['total_clicks']:,.0f}")
    md.append(f"- **Total Conversions:** {exec_summary['total_conversions']:,.0f}")
    md.append(f"- **Total Cost:** {fmt_currency(exec_summary['total_cost'])}")
    md.append(f"- **Total Revenue:** {fmt_currency(exec_summary['total_revenue'])}")
    md.append(f"- **Overall CTR:** {fmt_pct(exec_summary['overall_ctr'])}")
    md.append(f"- **Overall CPC:** {fmt_currency(exec_summary['overall_cpc'])}")
    md.append(f"- **Overall Conversion Rate:** {fmt_pct(exec_summary['overall_conversion_rate'])}")
    md.append(f"- **Overall ROAS:** {exec_summary['overall_roas']:.2f}")
    md.append(f"- **Overall Cost per Conversion:** {fmt_currency(exec_summary['overall_cost_per_conversion'])}\n")

    md.append("## Top Campaigns\n")
    md.append("### Top 5 by ROAS\n")
    md.append(to_markdown_table(top_roas[['campaign_name', 'roas', 'revenue']]))
    md.append("### Top 5 by Revenue\n")
    md.append(to_markdown_table(top_rev[['campaign_name', 'revenue', 'roas']]))
    md.append("### Top 5 by Conversion Rate\n")
    md.append(to_markdown_table(top_cvr[['campaign_name', 'conversion_rate', 'conversions']]))

    md.append("## Underperforming Campaigns\n")
    md.append(
        f"*Classification rules: High CTR/Low CVR — CTR above dataset mean and CVR below "
        f"{LOW_CVR_THRESHOLD:.0%}. High Cost/Low ROAS — cost above dataset median and ROAS "
        f"below {LOW_ROAS_THRESHOLD}. See [docs/REPORTING.md](../docs/REPORTING.md) for details.*\n"
    )
    md.append("### High CTR, Low Conversion Rate\n")
    md.append(to_markdown_table(high_ctr_low_cvr[['campaign_name', 'ctr', 'conversion_rate', 'cost']]))
    md.append("### High Cost, Low ROAS\n")
    md.append(to_markdown_table(high_cost_low_roas[['campaign_name', 'cost', 'roas', 'revenue']]))
    md.append("### Highest Cost per Conversion\n")
    md.append(to_markdown_table(high_cpa[['campaign_name', 'cost_per_conversion', 'conversions', 'cost']]))

    md.append("## Category Performance\n")
    md.append("### Top Categories by Revenue\n")
    md.append(to_markdown_table(top_cat_rev[['category', 'revenue', 'roas']]))
    md.append("### Top Categories by ROAS\n")
    md.append(to_markdown_table(top_cat_roas[['category', 'roas', 'revenue']]))
    md.append("### Categories with Weakest Conversion Rate\n")
    md.append(to_markdown_table(weak_cat_cvr[['category', 'conversion_rate', 'conversions']]))

    md.append("## Data Quality Notes\n")
    md.append(
        "This report relies on data that has passed automated upstream validation and metric "
        "quality tests. Key assumptions enforced during pipeline execution:"
    )
    md.append("- All metrics are strictly non-negative.")
    md.append("- Safe division (NULLIF) prevents division-by-zero errors.")
    md.append(
        "- An impression-based attribution model is used to ensure daily funnel consistency "
        "(clicks <= impressions, conversions <= clicks).\n"
    )

    md.append("## Interpretation Notes\n")
    md.append(
        f"- **CTR (Click-Through Rate):** The percentage of impressions that led to a click. "
        f"A high CTR indicates the ad is engaging."
    )
    md.append(
        f"- **CPC (Cost Per Click):** How much is paid on average for each ad click ({CURRENCY_CODE})."
    )
    md.append(
        "- **Conversion Rate:** The percentage of clicks that resulted in a purchase. "
        "A high rate indicates the product or landing page is effective."
    )
    md.append(
        f"- **ROAS (Return on Ad Spend):** Revenue generated per {CURRENCY_CODE} spent. "
        f"ROAS < {LOW_ROAS_THRESHOLD} is considered weak; above {HIGH_ROAS_THRESHOLD} is strong."
    )
    md.append(
        f"- **Cost per Conversion:** The average cost to acquire one conversion ({CURRENCY_CODE})."
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    logger.info(f"Report successfully generated at {report_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    generate_report()
