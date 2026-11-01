-- STAGING: Products

SELECT
    product_id,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    CAST(price AS DECIMAL(10, 2)) AS price
FROM raw_products;