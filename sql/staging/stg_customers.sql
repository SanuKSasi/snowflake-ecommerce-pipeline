-- STAGING: Customers

SELECT
    customer_id,
    TRIM(first_name) AS first_name,
    TRIM(last_name) AS last_name,
    LOWER(TRIM(email)) AS email,
    TRIM(city) AS city,
    CAST(signup_date AS DATE) AS signup_date
FROM raw_customers;