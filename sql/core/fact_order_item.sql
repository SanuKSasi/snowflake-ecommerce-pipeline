-- CORE: Order Item Fact

SELECT
    ROW_NUMBER() OVER (ORDER BY oi.order_id, oi.product_id) AS order_item_key,
    fo.order_key,
    dp.product_key,
    oi.quantity,
    oi.unit_price,
    ROUND(oi.quantity * oi.unit_price, 2) AS sales_amount
FROM stg_order_items oi
JOIN fact_order fo
    ON oi.order_id = fo.order_id
JOIN dim_product dp
    ON oi.product_id = dp.product_id;