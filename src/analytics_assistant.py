"""Rule-based analytics assistant.

Converts aggregated analytical mart metrics into business-readable insights
using a deterministic classification model.  No external LLM APIs are used.

Classification logic:
- Each campaign is scored against absolute thresholds (imported from config)
  combined with dataset-relative context (e.g. median cost).
- Each campaign receives exactly one classification:
    critical    → high spend + weak ROAS (immediate attention required)
    warning     → expensive traffic + low conversion rate
    monitor     → mixed signals (e.g. strong ROAS but weak CVR)
    opportunity → strong ROAS, candidate for scaling
- The highest-severity classification is emitted; conflicting signals are
  synthesised into a single, coherent recommendation.
"""
import duckdb
import pandas as pd
import logging
from src.paths import DATABASE_PATH, PROJECT_ROOT
from src.config import (
    CURRENCY_SYMBOL,
    CURRENCY_CODE,
    DATASET_SEED,
    REPORTING_PERIOD,
    LOW_ROAS_THRESHOLD,
    HIGH_ROAS_THRESHOLD,
    EXCEPTIONAL_ROAS_THRESHOLD,
    LOW_CVR_THRESHOLD,
    HIGH_CPC_THRESHOLD,
)

logger = logging.getLogger(__name__)

# Classification severity order (highest first)
_SEVERITY = {"critical": 0, "warning": 1, "monitor": 2, "opportunity": 3}


def _classify_campaign(row, median_cost: float) -> tuple[str, str]:
    """Return (classification_label, insight_text) for a single campaign row.

    At most one classification is returned — the highest severity that applies.
    Metrics used: roas, cvr, cpc, cost.  All comparisons use absolute thresholds
    from config to avoid relative distortion when ROAS values are extreme.
    """
    name = row['campaign_name']
    roas = row['roas']
    cvr = row['cvr']
    cpc = row['cpc']
    cost = row['cost']
    ctr = row['ctr']

    # Guard against NULL metrics (can happen for campaigns with zero clicks)
    roas_ok = pd.notnull(roas)
    cvr_ok = pd.notnull(cvr)
    cpc_ok = pd.notnull(cpc)
    ctr_ok = pd.notnull(ctr)

    # --- CRITICAL: high spend, weak ROAS ---
    if roas_ok and cost > median_cost and roas < LOW_ROAS_THRESHOLD:
        roas_str = f"{roas:.2f}"
        cost_str = f"{cost:,.2f} {CURRENCY_SYMBOL}"
        return (
            "critical",
            f"**{name}** — Critical: High spend ({cost_str}) with weak ROAS ({roas_str}). "
            f"Campaign is burning budget with low return. Review or pause to prevent further loss.",
        )

    # --- WARNING: expensive clicks + low conversion rate ---
    if cpc_ok and cvr_ok and cpc > HIGH_CPC_THRESHOLD and cvr < LOW_CVR_THRESHOLD:
        cpc_str = f"{cpc:.2f} {CURRENCY_SYMBOL}"
        cvr_str = f"{cvr:.2%}"
        roas_note = f" ROAS: {roas:.2f}." if roas_ok else ""
        return (
            "warning",
            f"**{name}** — Warning: Expensive clicks (CPC: {cpc_str}) combined with a low "
            f"conversion rate ({cvr_str}).{roas_note} Refine audience targeting or pause "
            f"until the landing page is improved.",
        )

    # --- MONITOR: strong ROAS but weak CVR (mixed signal) ---
    if roas_ok and cvr_ok and roas >= HIGH_ROAS_THRESHOLD and cvr < LOW_CVR_THRESHOLD:
        roas_str = f"{roas:.2f}"
        cvr_str = f"{cvr:.2%}"
        return (
            "monitor",
            f"**{name}** — Monitor: Strong ROAS ({roas_str}) but below-target conversion rate "
            f"({cvr_str}). Preserve current spend while testing targeting and landing-page "
            f"improvements before scaling.",
        )

    # --- MONITOR: high CTR, low CVR (traffic mismatch) ---
    if ctr_ok and cvr_ok and cvr < LOW_CVR_THRESHOLD:
        cvr_str = f"{cvr:.2%}"
        ctr_str = f"{ctr:.2%}"
        return (
            "monitor",
            f"**{name}** — Monitor: High CTR ({ctr_str}) but low conversion rate ({cvr_str}). "
            f"Users engage with the ad but do not purchase. Check product-audience fit and "
            f"landing page relevance.",
        )

    # --- OPPORTUNITY: strong or exceptional ROAS ---
    if roas_ok and roas >= EXCEPTIONAL_ROAS_THRESHOLD:
        roas_str = f"{roas:.2f}"
        return (
            "opportunity",
            f"**{name}** — Opportunity: Exceptional ROAS ({roas_str}). "
            f"This campaign generates outstanding revenue relative to cost. "
            f"Candidate for careful budget increase.",
        )

    if roas_ok and roas >= HIGH_ROAS_THRESHOLD:
        roas_str = f"{roas:.2f}"
        return (
            "opportunity",
            f"**{name}** — Opportunity: Strong ROAS ({roas_str}). "
            f"Campaign performs well. Monitor for saturation before scaling.",
        )

    # No significant signal → no insight emitted for this campaign
    return (None, None)


def generate_insights(db_path=DATABASE_PATH, output_dir=PROJECT_ROOT / "reports"):
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "analytics_insights.md"

    conn = duckdb.connect(str(db_path))

    exec_summary = conn.execute("""
        SELECT 
            SUM(impressions) as total_impressions,
            SUM(clicks) as total_clicks,
            SUM(conversions) as total_conversions,
            SUM(cost) as total_cost,
            SUM(revenue) as total_revenue,
            SUM(clicks) / NULLIF(SUM(impressions), 0) as avg_ctr,
            SUM(cost) / NULLIF(SUM(clicks), 0) as avg_cpc,
            SUM(conversions) / NULLIF(SUM(clicks), 0) as avg_cvr,
            SUM(revenue) / NULLIF(SUM(cost), 0) as avg_roas
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
            SUM(cost) / NULLIF(SUM(clicks), 0) as cpc,
            SUM(conversions) / NULLIF(SUM(clicks), 0) as cvr,
            SUM(revenue) / NULLIF(SUM(cost), 0) as roas
        FROM daily_campaign_performance
        GROUP BY campaign_name
        ORDER BY campaign_name
    """).df()

    cat_agg = conn.execute("""
        SELECT 
            category,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(conversions) as conversions,
            SUM(cost) as cost,
            SUM(revenue) as revenue,
            SUM(clicks) / NULLIF(SUM(impressions), 0) as ctr,
            SUM(cost) / NULLIF(SUM(clicks), 0) as cpc,
            SUM(conversions) / NULLIF(SUM(clicks), 0) as cvr,
            SUM(revenue) / NULLIF(SUM(cost), 0) as roas
        FROM category_performance
        GROUP BY category
        ORDER BY category
    """).df()

    conn.close()

    median_cost = camp_agg['cost'].median() if not camp_agg.empty else 0.0

    # Build classified campaign insights — one entry per campaign
    classified: list[tuple[int, str, str]] = []  # (severity_rank, label, text)
    for _, row in camp_agg.iterrows():
        label, text = _classify_campaign(row, median_cost)
        if label is not None:
            classified.append((_SEVERITY[label], label, text))

    # Sort by severity (critical first), then alphabetically within tier
    classified.sort(key=lambda x: (x[0], x[2]))

    # Split by classification for readable output
    critical_items = [t for t in classified if t[1] == "critical"]
    warning_items = [t for t in classified if t[1] == "warning"]
    monitor_items = [t for t in classified if t[1] == "monitor"]
    opportunity_items = [t for t in classified if t[1] == "opportunity"]

    # Category insights
    avg_roas = float(exec_summary['avg_roas'] or 0.0)
    avg_cvr = float(exec_summary['avg_cvr'] or 0.0)

    cat_opportunity = []
    cat_risk = []
    for _, row in cat_agg.iterrows():
        cat = row['category']
        roas = row['roas']
        cvr = row['cvr']
        if pd.notnull(roas) and roas >= HIGH_ROAS_THRESHOLD:
            cat_opportunity.append(
                f"- **{cat}**: ROAS {roas:.2f} — strong category performance. "
                f"Consider increasing product coverage and ad investment."
            )
        elif pd.notnull(roas) and roas < LOW_ROAS_THRESHOLD:
            cat_risk.append(
                f"- **{cat}**: ROAS {roas:.2f} — below target. "
                f"Review product pricing, catalog relevance and ad creative."
            )

    # Build Markdown
    md = []
    md.append("# Analytics Assistant Insights\n")
    md.append(
        "*(Rule-based analytics assistant. No external LLM APIs were used. "
        "Classifications are deterministic and based on fixed thresholds — see "
        "[docs/REPORTING.md](../docs/REPORTING.md).)*\n"
    )
    md.append(f"**Dataset Seed:** {DATASET_SEED}  ")
    md.append(f"**Reporting Period:** {REPORTING_PERIOD}  ")
    md.append(f"**Currency:** {CURRENCY_CODE} ({CURRENCY_SYMBOL})\n")

    md.append("## Threshold Reference\n")
    md.append(f"| Threshold | Value |")
    md.append(f"|-|-|")
    md.append(f"| Weak ROAS (< ) | {LOW_ROAS_THRESHOLD} |")
    md.append(f"| Strong ROAS (> ) | {HIGH_ROAS_THRESHOLD} |")
    md.append(f"| Exceptional ROAS (> ) | {EXCEPTIONAL_ROAS_THRESHOLD} |")
    md.append(f"| Low CVR (< ) | {LOW_CVR_THRESHOLD:.0%} |")
    md.append(f"| High CPC (> ) | {HIGH_CPC_THRESHOLD} {CURRENCY_SYMBOL} |\n")

    md.append("## Campaign Insights\n")

    if not classified:
        md.append("No significant campaign signals detected with current thresholds.\n")
    else:
        if critical_items:
            md.append("### 🔴 Critical\n")
            md.extend([f"- {t[2]}" for t in critical_items])
            md.append("")
        if warning_items:
            md.append("### 🟠 Warning\n")
            md.extend([f"- {t[2]}" for t in warning_items])
            md.append("")
        if monitor_items:
            md.append("### 🟡 Monitor\n")
            md.extend([f"- {t[2]}" for t in monitor_items])
            md.append("")
        if opportunity_items:
            md.append("### 🟢 Opportunity\n")
            md.extend([f"- {t[2]}" for t in opportunity_items])
            md.append("")

    md.append("## Category Insights\n")
    if cat_opportunity:
        md.append("### Opportunities\n")
        md.extend(cat_opportunity)
        md.append("")
    if cat_risk:
        md.append("### Risks\n")
        md.extend(cat_risk)
        md.append("")
    if not cat_opportunity and not cat_risk:
        md.append("Category performance is broadly within the target ROAS range.\n")

    md.append("## Limitations\n")
    md.append(
        "- Insights use absolute thresholds from `src/config.py` combined with dataset-relative "
        "context (e.g. median campaign cost)."
    )
    md.append("- Based on synthetic data only — findings do not reflect real campaign behaviour.")
    md.append(
        "- The assistant does not model externalities such as seasonality, creative quality, "
        "or competitive pressure."
    )

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    logger.info(f"Analytics insights successfully generated at {report_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    generate_insights()
