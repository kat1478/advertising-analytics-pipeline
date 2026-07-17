import duckdb
import pytest
from src.generate_data import main as generate_data_main
from src.load_raw import load_raw_data
from src.run_sql import execute_sql_files
from src.paths import PROJECT_ROOT

@pytest.fixture(scope="module")
def setup_db(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("metrics_db")
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    generate_data_main(output_dir=raw_dir)
    
    db_path = tmp_path / "ads.duckdb"
    load_raw_data(db_path=db_path, raw_dir=raw_dir)
    
    sql_dir = PROJECT_ROOT / "sql"
    execute_sql_files(db_path=db_path, sql_dir=sql_dir)
    
    return db_path

# daily_campaign_performance tests
def test_daily_campaign_exists_and_not_empty(setup_db):
    conn = duckdb.connect(str(setup_db))
    count = conn.execute("SELECT COUNT(*) FROM daily_campaign_performance").fetchone()[0]
    conn.close()
    assert count > 0, "daily_campaign_performance is empty"

def test_daily_campaign_no_duplicates(setup_db):
    conn = duckdb.connect(str(setup_db))
    dups = conn.execute("SELECT COUNT(*) FROM (SELECT event_date, campaign_id FROM daily_campaign_performance GROUP BY 1, 2 HAVING COUNT(*) > 1)").fetchone()[0]
    conn.close()
    assert dups == 0, "Duplicates found in daily_campaign_performance"

def test_daily_campaign_counts_valid(setup_db):
    conn = duckdb.connect(str(setup_db))
    res = conn.execute("SELECT impressions, clicks, conversions, cost, revenue FROM daily_campaign_performance").fetchall()
    for row in res:
        imps, clks, convs, cost, rev = row
        assert imps >= 0, "impressions < 0"
        assert clks >= 0, "clicks < 0"
        assert convs >= 0, "conversions < 0"
        assert cost >= 0, "cost < 0"
        assert rev >= 0, "revenue < 0"
        assert clks <= imps, "clicks > impressions"
        assert convs <= clks, "conversions > clicks"
    conn.close()

def test_daily_campaign_metric_ranges(setup_db):
    conn = duckdb.connect(str(setup_db))
    res = conn.execute("SELECT ctr, conversion_rate, cpc, roas, cost_per_conversion FROM daily_campaign_performance").fetchall()
    for row in res:
        ctr, conv_rate, cpc, roas, cpa = row
        if ctr is not None:
            assert 0 <= ctr <= 1, "CTR out of range"
        if conv_rate is not None:
            assert 0 <= conv_rate <= 1, "Conversion rate out of range"
        if cpc is not None:
            assert cpc >= 0, "CPC < 0"
        if roas is not None:
            assert roas >= 0, "ROAS < 0"
        if cpa is not None:
            assert cpa >= 0, "Cost per conversion < 0"
    conn.close()

# category_performance tests
def test_category_exists_and_not_empty(setup_db):
    conn = duckdb.connect(str(setup_db))
    count = conn.execute("SELECT COUNT(*) FROM category_performance").fetchone()[0]
    conn.close()
    assert count > 0, "category_performance is empty"

def test_category_no_duplicates(setup_db):
    conn = duckdb.connect(str(setup_db))
    dups = conn.execute("SELECT COUNT(*) FROM (SELECT category FROM category_performance GROUP BY 1 HAVING COUNT(*) > 1)").fetchone()[0]
    conn.close()
    assert dups == 0, "Duplicates found in category_performance"

def test_category_counts_valid(setup_db):
    conn = duckdb.connect(str(setup_db))
    res = conn.execute("SELECT impressions, clicks, conversions, cost, revenue FROM category_performance").fetchall()
    for row in res:
        imps, clks, convs, cost, rev = row
        assert imps >= 0
        assert clks >= 0
        assert convs >= 0
        assert cost >= 0
        assert rev >= 0
        assert clks <= imps
        assert convs <= clks
    conn.close()

def test_category_metric_ranges(setup_db):
    conn = duckdb.connect(str(setup_db))
    res = conn.execute("SELECT ctr, conversion_rate, cpc, roas, cost_per_conversion FROM category_performance").fetchall()
    for row in res:
        ctr, conv_rate, cpc, roas, cpa = row
        if ctr is not None:
            assert 0 <= ctr <= 1
        if conv_rate is not None:
            assert 0 <= conv_rate <= 1
        if cpc is not None:
            assert cpc >= 0
        if roas is not None:
            assert roas >= 0
        if cpa is not None:
            assert cpa >= 0
    conn.close()

# fact_ad_events tests
def test_fact_table_exists_and_not_empty(setup_db):
    conn = duckdb.connect(str(setup_db))
    count = conn.execute("SELECT COUNT(*) FROM fact_campaign_product_daily").fetchone()[0]
    conn.close()
    assert count > 0, "fact_campaign_product_daily is empty"

def test_fact_table_no_duplicates(setup_db):
    conn = duckdb.connect(str(setup_db))
    dups = conn.execute("SELECT COUNT(*) FROM (SELECT event_date, campaign_id, product_id FROM fact_campaign_product_daily GROUP BY 1, 2, 3 HAVING COUNT(*) > 1)").fetchone()[0]
    conn.close()
    assert dups == 0, "Duplicates found in fact_campaign_product_daily"

def test_fact_table_cost_non_negative(setup_db):
    conn = duckdb.connect(str(setup_db))
    res = conn.execute("SELECT cost FROM fact_campaign_product_daily").fetchall()
    for row in res:
        cost = row[0]
        assert cost >= 0, "Cost allocation should be non-negative"
    conn.close()

def test_fact_table_total_allocated_cost(setup_db):
    conn = duckdb.connect(str(setup_db))
    allocated_costs = conn.execute("""
        SELECT event_date, campaign_id, SUM(cost) as total_allocated 
        FROM fact_campaign_product_daily 
        GROUP BY 1, 2
    """).fetchall()
    
    source_costs = conn.execute("""
        SELECT event_date, campaign_id, SUM(cost) as source_cost
        FROM stg_costs
        GROUP BY 1, 2
    """).fetchall()
    
    conn.close()
    
    source_map = {(row[0], row[1]): row[2] for row in source_costs}
    
    for row in allocated_costs:
        event_date, campaign_id, alloc_cost = row
        src_cost = source_map.get((event_date, campaign_id), 0.0)
        assert abs(alloc_cost - src_cost) < 0.01, f"Allocated cost {alloc_cost} mismatch with source cost {src_cost}"
