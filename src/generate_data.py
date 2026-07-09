import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from src.paths import RAW_DATA_DIR
from src.config import DEFAULT_RANDOM_SEED

logger = logging.getLogger(__name__)

def generate_campaigns(seed, num_campaigns=20):
    np.random.seed(seed)
    campaigns = []
    channels = ['Search', 'Social', 'Display', 'Video', 'Email']
    segments = ['Youth', 'Adults', 'Seniors', 'All']
    
    start_date = datetime(2023, 1, 1)
    
    for i in range(1, num_campaigns + 1):
        c_start = start_date + timedelta(days=int(np.random.randint(0, 180)))
        c_end = c_start + timedelta(days=int(np.random.randint(14, 90)))
        campaigns.append({
            'campaign_id': f'C{i:03d}',
            'campaign_name': f'Campaign_{i}',
            'channel': np.random.choice(channels),
            'start_date': c_start.strftime('%Y-%m-%d'),
            'end_date': c_end.strftime('%Y-%m-%d'),
            'budget': round(np.random.uniform(1000, 50000), 2),
            'target_segment': np.random.choice(segments)
        })
    return pd.DataFrame(campaigns)

def generate_products(seed, num_products=200):
    np.random.seed(seed + 1)
    products = []
    categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Toys']
    
    for i in range(1, num_products + 1):
        products.append({
            'product_id': f'P{i:04d}',
            'product_name': f'Product_{i}',
            'category': np.random.choice(categories),
            'price': round(np.random.uniform(10, 1000), 2)
        })
    return pd.DataFrame(products)

def generate_impressions(seed, campaigns_df, products_df, num_impressions=10000):
    np.random.seed(seed + 2)
    segments = ['Youth', 'Adults', 'Seniors', 'All']
    
    c_ids = campaigns_df['campaign_id'].tolist()
    p_ids = products_df['product_id'].tolist()
    
    base_time = datetime(2023, 6, 1)
    
    impressions = pd.DataFrame({
        'impression_id': [f'I{i:06d}' for i in range(1, num_impressions + 1)],
        'campaign_id': np.random.choice(c_ids, num_impressions),
        'product_id': np.random.choice(p_ids, num_impressions),
        'user_segment': np.random.choice(segments, num_impressions),
    })
    
    seconds_in_30_days = 30 * 24 * 60 * 60
    random_seconds = np.random.randint(0, seconds_in_30_days, num_impressions)
    impressions['event_timestamp'] = [
        (base_time + timedelta(seconds=int(s))).strftime('%Y-%m-%d %H:%M:%S') 
        for s in random_seconds
    ]
    
    return impressions

def generate_clicks(seed, impressions_df, ctr=0.05):
    np.random.seed(seed + 3)
    
    num_impressions = len(impressions_df)
    is_clicked = np.random.random(num_impressions) < ctr
    
    clicks_df = impressions_df[is_clicked].copy()
    clicks_df = clicks_df[['impression_id', 'campaign_id', 'product_id', 'event_timestamp']].rename(
        columns={'event_timestamp': 'imp_timestamp'}
    )
    
    num_clicks = len(clicks_df)
    clicks_df['click_id'] = [f'CK{i:06d}' for i in range(1, num_clicks + 1)]
    
    clicks_df['event_timestamp'] = pd.to_datetime(clicks_df['imp_timestamp']) + pd.to_timedelta(np.random.randint(1, 300, num_clicks), unit='s')
    clicks_df['event_timestamp'] = clicks_df['event_timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return clicks_df[['click_id', 'impression_id', 'campaign_id', 'product_id', 'event_timestamp']]

def generate_conversions(seed, clicks_df, products_df, cvr=0.1):
    np.random.seed(seed + 4)
    
    num_clicks = len(clicks_df)
    is_converted = np.random.random(num_clicks) < cvr
    
    conv_df = clicks_df[is_converted].copy()
    conv_df = conv_df.merge(products_df[['product_id', 'price']], on='product_id', how='left')
    
    num_conv = len(conv_df)
    conv_df['conversion_id'] = [f'CV{i:06d}' for i in range(1, num_conv + 1)]
    
    conv_df['event_timestamp'] = pd.to_datetime(conv_df['event_timestamp']) + pd.to_timedelta(np.random.randint(60, 86400, num_conv), unit='s')
    conv_df['event_timestamp'] = conv_df['event_timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    conv_df['revenue'] = conv_df['price'] * np.random.randint(1, 4, num_conv)
    
    return conv_df[['conversion_id', 'click_id', 'campaign_id', 'product_id', 'event_timestamp', 'revenue']]

def generate_costs(seed, impressions_df):
    np.random.seed(seed + 5)
    
    df = impressions_df.copy()
    df['event_date'] = pd.to_datetime(df['event_timestamp']).dt.strftime('%Y-%m-%d')
    
    daily_impressions = df.groupby(['campaign_id', 'event_date']).size().reset_index(name='imps')
    daily_impressions['cost'] = round(daily_impressions['imps'] * np.random.uniform(0.01, 0.05, len(daily_impressions)), 2)
    
    return daily_impressions[['campaign_id', 'event_date', 'cost']]

def main(output_dir=RAW_DATA_DIR):
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Generating synthetic data...")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    seed = DEFAULT_RANDOM_SEED
    
    campaigns = generate_campaigns(seed)
    products = generate_products(seed)
    impressions = generate_impressions(seed, campaigns, products)
    clicks = generate_clicks(seed, impressions)
    conversions = generate_conversions(seed, clicks, products)
    costs = generate_costs(seed, impressions)
    
    campaigns.to_csv(output_dir / "campaigns.csv", index=False)
    products.to_csv(output_dir / "products.csv", index=False)
    impressions.to_csv(output_dir / "impressions.csv", index=False)
    clicks.to_csv(output_dir / "clicks.csv", index=False)
    costs.to_csv(output_dir / "costs.csv", index=False)
    conversions.to_csv(output_dir / "conversions.csv", index=False)
    
    logger.info(f"Generated {len(campaigns)} campaigns")
    logger.info(f"Generated {len(products)} products")
    logger.info(f"Generated {len(impressions)} impressions")
    logger.info(f"Generated {len(clicks)} clicks")
    logger.info(f"Generated {len(conversions)} conversions")
    logger.info(f"Generated {len(costs)} daily cost records")
    logger.info(f"Data successfully saved to {output_dir}")

if __name__ == "__main__":
    main()
