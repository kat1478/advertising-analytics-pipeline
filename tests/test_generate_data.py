import pandas as pd
from src.generate_data import main

def test_generate_data_deterministic(tmp_path):
    main(output_dir=tmp_path)
    
    expected_files = [
        "campaigns.csv",
        "products.csv",
        "impressions.csv",
        "clicks.csv",
        "costs.csv",
        "conversions.csv"
    ]
    for f in expected_files:
        assert (tmp_path / f).exists(), f"{f} should exist"
        
    campaigns = pd.read_csv(tmp_path / "campaigns.csv")
    products = pd.read_csv(tmp_path / "products.csv")
    impressions = pd.read_csv(tmp_path / "impressions.csv")
    clicks = pd.read_csv(tmp_path / "clicks.csv")
    costs = pd.read_csv(tmp_path / "costs.csv")
    conversions = pd.read_csv(tmp_path / "conversions.csv")
    
    assert not campaigns.empty
    assert not products.empty
    assert not impressions.empty
    assert not clicks.empty
    assert not costs.empty
    assert not conversions.empty
    
    assert 'campaign_name' in campaigns.columns
    assert 'product_name' in products.columns
    assert 'impression_id' in impressions.columns
    assert 'click_id' in clicks.columns
    assert 'cost' in costs.columns
    assert 'revenue' in conversions.columns
    
    assert len(clicks) < len(impressions)
    assert len(conversions) < len(clicks)
    
    assert clicks['impression_id'].isin(impressions['impression_id']).all()
    assert conversions['click_id'].isin(clicks['click_id']).all()
    
    assert (costs['cost'] >= 0).all()
    assert (conversions['revenue'] >= 0).all()
    
    tmp_path2 = tmp_path / "run2"
    tmp_path2.mkdir()
    main(output_dir=tmp_path2)
    
    campaigns2 = pd.read_csv(tmp_path2 / "campaigns.csv")
    pd.testing.assert_frame_equal(campaigns, campaigns2)


def test_generate_data_roas_plausibility(tmp_path):
    """Overall ROAS must be within a plausible demonstration range."""
    import duckdb
    from src.load_raw import load_raw_data
    from src.run_sql import execute_sql_files
    from src.paths import PROJECT_ROOT

    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    main(output_dir=raw_dir)

    db_path = tmp_path / "ads.duckdb"
    load_raw_data(db_path=db_path, raw_dir=raw_dir)
    execute_sql_files(db_path=db_path, sql_dir=PROJECT_ROOT / "sql")

    conn = duckdb.connect(str(db_path))
    result = conn.execute("""
        SELECT
            SUM(revenue) / NULLIF(SUM(cost), 0) AS overall_roas,
            MIN(SUM(revenue) / NULLIF(SUM(cost), 0)) OVER () AS min_campaign_roas,
            MAX(SUM(revenue) / NULLIF(SUM(cost), 0)) OVER () AS max_campaign_roas
        FROM daily_campaign_performance
        GROUP BY campaign_name
        ORDER BY overall_roas
        LIMIT 1
    """).fetchone()

    camp_roas = conn.execute("""
        SELECT
            campaign_name,
            SUM(revenue) / NULLIF(SUM(cost), 0) AS roas
        FROM daily_campaign_performance
        GROUP BY campaign_name
        ORDER BY roas
    """).fetchall()
    conn.close()

    roas_values = [row[1] for row in camp_roas if row[1] is not None]
    overall_roas = sum(v for v in roas_values) / len(roas_values) if roas_values else 0

    # Overall average ROAS should be within a plausible demonstration range
    assert 0.5 <= overall_roas <= 30.0, (
        f"Overall mean campaign ROAS {overall_roas:.2f} is outside plausible range [0.5, 30]"
    )

    # There must be at least one weak campaign and one strong campaign
    min_roas = min(roas_values)
    max_roas = max(roas_values)
    assert min_roas < 3.0, (
        f"Expected at least one campaign with ROAS < 3.0, got min={min_roas:.2f}. "
        f"Data lacks analytical variety."
    )
    assert max_roas > 2.0, (
        f"Expected at least one campaign with ROAS > 2.0, got max={max_roas:.2f}. "
        f"Data lacks analytical variety."
    )
