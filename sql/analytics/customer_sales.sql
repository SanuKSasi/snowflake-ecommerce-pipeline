-- ANALYTICS: Customer Sales

SELECT
    fo.customer_key,
    COUNT(DISTINCT fo.order_key) AS orders,
    SUM(foi.quantity) AS items_sold,
    ROUND(SUM(foi.sales_amount), 2) AS revenue
FROM fact_order fo
JOIN fact_order_item foi
    ON fo.order_key = foi.order_key
GROUP BY fo.customer_key
ORDER BY revenue DESC;