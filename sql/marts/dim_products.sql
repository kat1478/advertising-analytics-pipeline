CREATE OR REPLACE TABLE dim_products AS
SELECT
    product_id,
    product_name,
    category,
    price
FROM stg_products;
