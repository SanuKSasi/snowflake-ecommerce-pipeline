from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = PROJECT_ROOT / "data" / "core"
ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"

ANALYTICS_DIR.mkdir(exist_ok=True)


def main():
    print("Creating ANALYTICS data models...\n")

    # Read CORE data
    dim_customer = pd.read_csv(
        CORE_DIR / "dim_customer.csv"
    )

    dim_product = pd.read_csv(
        CORE_DIR / "dim_product.csv"
    )

    fact_order = pd.read_csv(
        CORE_DIR / "fact_order.csv",
        parse_dates=["order_date"],
    )

    fact_order_item = pd.read_csv(
        CORE_DIR / "fact_order_item.csv"
    )

    # Join fact order items with orders and products
    sales = fact_order_item.merge(
        fact_order[
            ["order_key", "order_date", "customer_key", "status"]
        ],
        on="order_key",
        how="left",
        validate="many_to_one",
    )

    sales = sales.merge(
        dim_product[
            ["product_key", "product_name", "category"]
        ],
        on="product_key",
        how="left",
        validate="many_to_one",
    )

    # ---------------------------------------------------------
    # 1. DAILY SALES
    # ---------------------------------------------------------

    daily_sales = (
        sales.groupby("order_date")
        .agg(
            orders=("order_key", "nunique"),
            items_sold=("quantity", "sum"),
            revenue=("sales_amount", "sum"),
        )
        .reset_index()
    )

    daily_sales["revenue"] = daily_sales["revenue"].round(2)

    # ---------------------------------------------------------
    # 2. CUSTOMER SALES
    # ---------------------------------------------------------

    customer_sales = (
        sales.groupby("customer_key")
        .agg(
            orders=("order_key", "nunique"),
            items_sold=("quantity", "sum"),
            revenue=("sales_amount", "sum"),
        )
        .reset_index()
    )

    customer_sales["revenue"] = customer_sales["revenue"].round(2)

    # ---------------------------------------------------------
    # 3. PRODUCT PERFORMANCE
    # ---------------------------------------------------------

    product_performance = (
        sales.groupby(
            ["product_key", "product_name", "category"]
        )
        .agg(
            orders=("order_key", "nunique"),
            quantity_sold=("quantity", "sum"),
            revenue=("sales_amount", "sum"),
        )
        .reset_index()
    )

    product_performance["revenue"] = (
        product_performance["revenue"].round(2)
    )

    # ---------------------------------------------------------
    # 4. CATEGORY PERFORMANCE
    # ---------------------------------------------------------

    category_performance = (
        sales.groupby("category")
        .agg(
            orders=("order_key", "nunique"),
            quantity_sold=("quantity", "sum"),
            revenue=("sales_amount", "sum"),
        )
        .reset_index()
    )

    category_performance["revenue"] = (
        category_performance["revenue"].round(2)
    )

    # ---------------------------------------------------------
    # Write ANALYTICS tables
    # ---------------------------------------------------------

    daily_sales.to_csv(
        ANALYTICS_DIR / "daily_sales.csv",
        index=False,
    )

    customer_sales.to_csv(
        ANALYTICS_DIR / "customer_sales.csv",
        index=False,
    )

    product_performance.to_csv(
        ANALYTICS_DIR / "product_performance.csv",
        index=False,
    )

    category_performance.to_csv(
        ANALYTICS_DIR / "category_performance.csv",
        index=False,
    )

    print("ANALYTICS transformation completed.\n")

    print(f"DAILY_SALES          : {len(daily_sales):,}")
    print(f"CUSTOMER_SALES       : {len(customer_sales):,}")
    print(f"PRODUCT_PERFORMANCE  : {len(product_performance):,}")
    print(f"CATEGORY_PERFORMANCE : {len(category_performance):,}")


if __name__ == "__main__":
    main()