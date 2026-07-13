CREATE OR REPLACE TABLE stg_products AS
SELECT DISTINCT
    CAST(SUBSTR(product_id, 2) AS INTEGER) AS product_id,
    CAST(product_name AS VARCHAR) AS product_name,
    CAST(category AS VARCHAR) AS category,
    CAST(price AS DOUBLE) AS price
FROM raw_products;
