-- CORE: Order Fact

SELECT
    ROW_NUMBER() OVER (ORDER BY o.order_id) AS order_key,
    o.order_id,
    c.customer_key,
    o.order_date,
    o.status
FROM stg_orders o
JOIN dim_customer c
    ON o.customer_id = c.customer_id;