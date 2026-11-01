-- ANALYTICS: Product Performance

SELECT
    foi.product_key,
    dp.product_name,
    dp.category,
    COUNT(DISTINCT foi.order_key) AS orders,
    SUM(foi.quantity) AS quantity_sold,
    ROUND(SUM(foi.sales_amount), 2) AS revenue
FROM fact_order_item foi
JOIN dim_product dp
    ON foi.product_key = dp.product_key
GROUP BY
    foi.product_key,
    dp.product_name,
    dp.category
ORDER BY revenue DESC;