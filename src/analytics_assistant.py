import duckdb
import pandas as pd
from datetime import datetime
import logging
from src.paths import DATABASE_PATH, PROJECT_ROOT

logger = logging.getLogger(__name__)

# Configurable Thresholds defined as constants
HIGH_CTR_MULTIPLIER = 1.2
LOW_CVR_MULTIPLIER = 0.8
HIGH_ROAS_MULTIPLIER = 1.2
HIGH_CPC_MULTIPLIER = 1.2
LOW_ROAS_MULTIPLIER = 0.8
CAT_OPP_ROAS_MULTIPLIER = 1.1
CAT_RISK_ROAS_MULTIPLIER = 0.9

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
    
    avg_ctr = exec_summary['avg_ctr'] or 0.0
    avg_cvr = exec_summary['avg_cvr'] or 0.0
    avg_roas = exec_summary['avg_roas'] or 0.0
    avg_cpc = exec_summary['avg_cpc'] or 0.0
    median_cost = camp_agg['cost'].median() if not camp_agg.empty else 0.0
    
    campaign_insights = []
    actions = set()
    
    for _, row in camp_agg.iterrows():
        c = row['campaign_name']
        ctr, cvr, roas, cpc, cost = row['ctr'], row['cvr'], row['roas'], row['cpc'], row['cost']
        
        if pd.notnull(ctr) and pd.notnull(cvr) and ctr > avg_ctr * HIGH_CTR_MULTIPLIER and cvr < avg_cvr * LOW_CVR_MULTIPLIER:
            campaign_insights.append(f"- **{c}**: High CTR ({ctr:.2%}) but low conversion rate ({cvr:.2%}). Users click but do not convert. Potential targeting mismatch or weak landing page offer.")
            actions.add("- Review targeting and inspect landing page/product fit.")
            
        if pd.notnull(roas) and roas > avg_roas * HIGH_ROAS_MULTIPLIER:
            campaign_insights.append(f"- **{c}**: Strong ROAS ({roas:.2f}). Generates excellent revenue relative to cost. Candidate for budget increase.")
            actions.add("- Increase budget carefully for top-performing ROAS campaigns.")
            
        if pd.notnull(cpc) and pd.notnull(cvr) and cpc > avg_cpc * HIGH_CPC_MULTIPLIER and cvr < avg_cvr * LOW_CVR_MULTIPLIER:
            campaign_insights.append(f"- **{c}**: Expensive clicks (CPC: ${cpc:.2f}) and low conversion rate ({cvr:.2%}). Highly inefficient. Audience targeting should be refined or ad paused.")
            actions.add("- Pause or reduce spend on high CPC, low conversion campaigns.")
            
        if pd.notnull(cost) and pd.notnull(roas) and cost > median_cost and roas < avg_roas * LOW_ROAS_MULTIPLIER:
            campaign_insights.append(f"- **{c}**: High spend (${cost:,.2f}) but low ROAS ({roas:.2f}). Burning budget with low return. Potential pause candidate.")
            actions.add("- Pause or optimize high-spend, low-ROAS campaigns immediately.")
            
    if not campaign_insights:
        campaign_insights.append("- No significant campaign outliers detected based on current thresholds.")
        
    category_insights = []
    for _, row in cat_agg.iterrows():
        cat = row['category']
        roas, cvr = row['roas'], row['cvr']
        
        if pd.notnull(roas) and roas > avg_roas * CAT_OPP_ROAS_MULTIPLIER:
            category_insights.append(f"- **{cat}**: Strong category opportunity with ROAS {roas:.2f}. Candidate for further investment.")
            actions.add("- Investigate category-level demand for high-performing product groups.")
            
        if pd.notnull(roas) and pd.notnull(cvr) and (roas < avg_roas * CAT_RISK_ROAS_MULTIPLIER or cvr < avg_cvr * 0.9):
            category_insights.append(f"- **{cat}**: Category risk detected (ROAS: {roas:.2f}, CVR: {cvr:.2%}). Requires further analysis of product catalog pricing or ad relevance.")
            actions.add("- Review product offerings and ad relevance in underperforming categories.")
            
    if not category_insights:
        category_insights.append("- Category performance is relatively uniform across the board.")
        
    if not actions:
        actions.add("- Continue monitoring performance trends.")

    md = []
    md.append("# Analytics Assistant Insights\n")
    md.append("*(Note: This is a deterministic, rule-based analytics assistant operating on aggregated data marts. No external LLM APIs were used.)*\n")
    md.append(f"**Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    md.append("## Campaign Insights\n")
    md.extend(campaign_insights)
    md.append("\n")
    
    md.append("## Category Insights\n")
    md.extend(category_insights)
    md.append("\n")
    
    md.append("## Suggested Actions\n")
    md.extend(sorted(list(actions)))
    md.append("\n")
    
    md.append("## Limitations\n")
    md.append("- Insights are generated using hardcoded logic thresholds compared against dataset averages.")
    md.append("- Findings are only as accurate as the underlying synthetic event attribution.")
    md.append("- This assistant does not interpret unmodeled externalities (e.g., seasonality, ad creatives).")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    logger.info(f"Analytics insights successfully generated at {report_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    generate_insights()
