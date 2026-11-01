
from snowflake.snowpark.functions import (
    col,
    trim,
    lower,
    upper,
    row_number,
    sum,
    count,
    count_distinct,
    avg
)
from snowflake.snowpark.window import Window

from src.utils.snowpark_session import get_snowpark_session


def transform_customers(session):

    customers = session.table("RAW.CUSTOMERS")

    transformed_customers = customers.select(
        col("CUSTOMER_ID"),
        trim(col("FIRST_NAME")).alias("FIRST_NAME"),
        trim(col("LAST_NAME")).alias("LAST_NAME"),
        lower(trim(col("EMAIL"))).alias("EMAIL"),
        trim(col("CITY")).alias("CITY"),
        col("SIGNUP_DATE").cast("DATE").alias("SIGNUP_DATE")
    )

    transformed_customers.write.mode("overwrite").save_as_table(
        "STAGING.STG_CUSTOMERS"
    )

    print("Customer transformation completed.")
    print(
        "STG_CUSTOMERS row count:",
        session.table("STAGING.STG_CUSTOMERS").count()
    )
    

def transform_products(session):

    products = session.table("RAW.PRODUCTS")

    transformed = products.select(
        col("PRODUCT_ID"),
        trim(col("PRODUCT_NAME")).alias("PRODUCT_NAME"),
        trim(col("CATEGORY")).alias("CATEGORY"),
        col("PRICE").cast("DECIMAL(10,2)").alias("PRICE")
    )

    transformed.write.mode("overwrite").save_as_table(
        "STAGING.STG_PRODUCTS"
    )

    print("Products transformation completed.")


def transform_orders(session):

    orders = session.table("RAW.ORDERS")

    transformed = orders.select(
        col("ORDER_ID"),
        col("CUSTOMER_ID"),
        col("ORDER_DATE").cast("DATE").alias("ORDER_DATE"),
        upper(trim(col("STATUS"))).alias("STATUS")
    )

    transformed.write.mode("overwrite").save_as_table(
        "STAGING.STG_ORDERS"
    )

    print("Orders transformation completed.")


def transform_order_items(session):

    order_items = session.table("RAW.ORDER_ITEMS")

    transformed = order_items.select(
        col("ORDER_ID"),
        col("PRODUCT_ID"),
        col("QUANTITY").cast("INTEGER").alias("QUANTITY"),
        col("UNIT_PRICE").cast("DECIMAL(10,2)").alias("UNIT_PRICE")
    )

    transformed.write.mode("overwrite").save_as_table(
        "STAGING.STG_ORDER_ITEMS"
    )

    print("Order items transformation completed.")

    print(
        "STG_ORDER_ITEMS row count:",
        session.table("STAGING.STG_ORDER_ITEMS").count()
    )
    
def transform_dim_customer(session):
    customers = session.table("STAGING.STG_CUSTOMERS")
    print("Customer source columns:", customers.columns)
    print("Customer source count:", customers.count())
    window_spec = Window.order_by(col("CUSTOMER_ID"))

    dim_customer = customers.select(
        row_number().over(window_spec).alias("CUSTOMER_KEY"),
        col("CUSTOMER_ID"),
        col("FIRST_NAME"),
        col("LAST_NAME"),
        col("EMAIL"),
        col("CITY"),
        col("SIGNUP_DATE")
    )
    print("Dimension columns:", dim_customer.columns)
    dim_customer.write.mode("overwrite").save_as_table(
        "CORE.DIM_CUSTOMER"
    )

    print(
        "DIM_CUSTOMER created. Row count:",
        session.table("CORE.DIM_CUSTOMER").count()
    )    

def transform_dim_product(session):

    products = session.table("STAGING.STG_PRODUCTS")

    window_spec = Window.order_by(col("PRODUCT_ID"))

    dim_product = products.select(
        row_number().over(window_spec).alias("PRODUCT_KEY"),
        col("PRODUCT_ID"),
        col("PRODUCT_NAME"),
        col("CATEGORY"),
        col("PRICE")
    )

    dim_product.write.mode("overwrite").save_as_table(
        "CORE.DIM_PRODUCT"
    )

    print(
        "DIM_PRODUCT created. Row count:",
        session.table("CORE.DIM_PRODUCT").count()
    )
    
def transform_fact_order(session):

    orders = session.table("STAGING.STG_ORDERS")
    customers = session.table("CORE.DIM_CUSTOMER")

    joined_orders = orders.join(
        customers,
        orders["CUSTOMER_ID"] == customers["CUSTOMER_ID"],
        "inner"
    )

    window_spec = Window.order_by(col("ORDER_ID"))

    fact_order = joined_orders.select(
        row_number().over(window_spec).alias("ORDER_KEY"),
        orders["ORDER_ID"],
        customers["CUSTOMER_KEY"],
        orders["ORDER_DATE"],
        orders["STATUS"]
    )

    fact_order.write.mode("overwrite").save_as_table(
        "CORE.FACT_ORDER"
    )

    print(
        "FACT_ORDER created. Row count:",
        session.table("CORE.FACT_ORDER").count()
    )

def transform_fact_order_item(session):

    order_items = session.table("STAGING.STG_ORDER_ITEMS")
    orders = session.table("CORE.FACT_ORDER")
    products = session.table("CORE.DIM_PRODUCT")

    joined_data = order_items.join(
        orders,
        order_items["ORDER_ID"] == orders["ORDER_ID"],
        "inner"
    ).join(
        products,
        order_items["PRODUCT_ID"] == products["PRODUCT_ID"],
        "inner"
    )

    window_spec = Window.order_by(
        order_items["ORDER_ID"],
        order_items["PRODUCT_ID"]
    )

    fact_order_item = joined_data.select(
        row_number().over(window_spec).alias("ORDER_ITEM_KEY"),
        orders["ORDER_KEY"],
        products["PRODUCT_KEY"],
        order_items["ORDER_ID"],
        order_items["PRODUCT_ID"],
        order_items["QUANTITY"],
        order_items["UNIT_PRICE"],
        (
            order_items["QUANTITY"] * order_items["UNIT_PRICE"]
        ).alias("SALES_AMOUNT")
    )

    fact_order_item.write.mode("overwrite").save_as_table(
        "CORE.FACT_ORDER_ITEM"
    )

    print(
        "FACT_ORDER_ITEM created. Row count:",
        session.table("CORE.FACT_ORDER_ITEM").count()
    )

def transform_daily_sales(session):

    fact_order = session.table("CORE.FACT_ORDER")
    fact_order_item = session.table("CORE.FACT_ORDER_ITEM")

    joined_data = fact_order.join(
        fact_order_item,
        fact_order["ORDER_KEY"] == fact_order_item["ORDER_KEY"],
        "inner"
    )

    daily_sales = joined_data.group_by(
        fact_order["ORDER_DATE"]
    ).agg(
        count_distinct(fact_order["ORDER_ID"]).alias("TOTAL_ORDERS"),
        sum(fact_order_item["QUANTITY"]).alias("TOTAL_QUANTITY"),
        sum(fact_order_item["SALES_AMOUNT"]).alias("TOTAL_REVENUE"),
        avg(fact_order_item["SALES_AMOUNT"]).alias("AVG_ITEM_VALUE")
    )

    daily_sales.write.mode("overwrite").save_as_table(
        "ANALYTICS.DAILY_SALES"
    )

    print(
        "DAILY_SALES created. Row count:",
        session.table("ANALYTICS.DAILY_SALES").count()
    ) 

def transform_customer_sales(session):

    customers = session.table("CORE.DIM_CUSTOMER")
    orders = session.table("CORE.FACT_ORDER")
    order_items = session.table("CORE.FACT_ORDER_ITEM")

    joined_data = orders.join(
        customers,
        orders["CUSTOMER_KEY"] == customers["CUSTOMER_KEY"],
        "inner"
    ).join(
        order_items,
        orders["ORDER_KEY"] == order_items["ORDER_KEY"],
        "inner"
    )

    customer_sales = joined_data.group_by(
        customers["CUSTOMER_KEY"],
        customers["CUSTOMER_ID"],
        customers["FIRST_NAME"],
        customers["LAST_NAME"],
        customers["CITY"]
    ).agg(
        count_distinct(orders["ORDER_ID"]).alias("TOTAL_ORDERS"),
        sum(order_items["QUANTITY"]).alias("TOTAL_QUANTITY"),
        sum(order_items["SALES_AMOUNT"]).alias("TOTAL_REVENUE")
    )

    customer_sales = customer_sales.with_column(
        "AVG_ORDER_VALUE",
        col("TOTAL_REVENUE") / col("TOTAL_ORDERS")
    )

    customer_sales.write.mode("overwrite").save_as_table(
        "ANALYTICS.CUSTOMER_SALES"
    )

    print(
        "CUSTOMER_SALES created. Row count:",
        session.table("ANALYTICS.CUSTOMER_SALES").count()
    )    

def transform_product_performance(session):

    products = session.table("CORE.DIM_PRODUCT")
    order_items = session.table("CORE.FACT_ORDER_ITEM")

    joined_data = products.join(
        order_items,
        products["PRODUCT_KEY"] == order_items["PRODUCT_KEY"],
        "inner"
    )

    product_performance = joined_data.group_by(
        products["PRODUCT_KEY"],
        products["PRODUCT_ID"],
        products["PRODUCT_NAME"],
        products["CATEGORY"],
        products["PRICE"]
    ).agg(
        count_distinct(order_items["ORDER_KEY"]).alias("TOTAL_ORDERS"),
        sum(order_items["QUANTITY"]).alias("TOTAL_QUANTITY"),
        sum(order_items["SALES_AMOUNT"]).alias("TOTAL_REVENUE"),
        avg(order_items["UNIT_PRICE"]).alias("AVG_SELLING_PRICE")
    )

    product_performance.write.mode("overwrite").save_as_table(
        "ANALYTICS.PRODUCT_PERFORMANCE"
    )

    print(
        "PRODUCT_PERFORMANCE created. Row count:",
        session.table("ANALYTICS.PRODUCT_PERFORMANCE").count()
    )

def transform_category_performance(session):

    products = session.table("CORE.DIM_PRODUCT")
    order_items = session.table("CORE.FACT_ORDER_ITEM")

    joined_data = products.join(
        order_items,
        products["PRODUCT_KEY"] == order_items["PRODUCT_KEY"],
        "inner"
    )

    category_performance = joined_data.group_by(
        products["CATEGORY"]
    ).agg(
        count_distinct(products["PRODUCT_KEY"]).alias("TOTAL_PRODUCTS"),
        count_distinct(order_items["ORDER_KEY"]).alias("TOTAL_ORDERS"),
        sum(order_items["QUANTITY"]).alias("TOTAL_QUANTITY"),
        sum(order_items["SALES_AMOUNT"]).alias("TOTAL_REVENUE")
    )

    category_performance.write.mode("overwrite").save_as_table(
        "ANALYTICS.CATEGORY_PERFORMANCE"
    )

    print(
        "CATEGORY_PERFORMANCE created. Row count:",
        session.table("ANALYTICS.CATEGORY_PERFORMANCE").count()
    )

if __name__ == "__main__":
    session = None
    try:
        session = get_snowpark_session()

        transform_customers(session)
        transform_products(session)
        transform_orders(session)
        transform_order_items(session)

        transform_dim_customer(session)
        transform_dim_product(session)
        transform_fact_order(session)
        transform_fact_order_item(session)
        
        transform_daily_sales(session)
        transform_customer_sales(session)
        transform_product_performance(session)
        transform_category_performance(session)

        print("\nAll transformations completed.")

    except Exception as error:
        print("Transformation failed:", error)
        raise

    finally:
        if session:
            session.close()