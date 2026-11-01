-- CORE: Customer Dimension

SELECT
    ROW_NUMBER() OVER (ORDER BY customer_id) AS customer_key,
    customer_id,
    first_name,
    last_name,
    email,
    city,
    signup_date
FROM stg_customers;