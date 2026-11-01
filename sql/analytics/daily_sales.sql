-- ANALYTICS: Daily Sales

SELECT
    fo.order_date,
    COUNT(DISTINCT fo.order_key) AS orders,
    SUM(foi.quantity) AS items_sold,
    ROUND(SUM(foi.sales_amount), 2) AS revenue
FROM fact_order fo
JOIN fact_order_item foi
    ON fo.order_key = foi.order_key
GROUP BY fo.order_date
ORDER BY fo.order_date;