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
