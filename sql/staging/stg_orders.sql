-- STAGING: Orders

SELECT
    order_id,
    customer_id,
    CAST(order_date AS DATE) AS order_date,
    UPPER(TRIM(status)) AS status
FROM raw_orders;