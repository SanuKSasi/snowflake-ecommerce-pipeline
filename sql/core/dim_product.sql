-- CORE: Product Dimension

SELECT
    ROW_NUMBER() OVER (ORDER BY product_id) AS product_key,
    product_id,
    product_name,
    category,
    price
FROM stg_products;