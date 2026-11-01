from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = PROJECT_ROOT / "data" / "core"
ANALYTICS_DIR = PROJECT_ROOT / "data" / "analytics"


def main():
    print("Starting ANALYTICS data-quality validation...\n")

    # Read CORE data
    fact_order = pd.read_csv(
        CORE_DIR / "fact_order.csv"
    )

    fact_order_item = pd.read_csv(
        CORE_DIR / "fact_order_item.csv"
    )

    # Read ANALYTICS data
    daily_sales = pd.read_csv(
        ANALYTICS_DIR / "daily_sales.csv",
        parse_dates=["order_date"],
    )

    customer_sales = pd.read_csv(
        ANALYTICS_DIR / "customer_sales.csv"
    )

    product_performance = pd.read_csv(
        ANALYTICS_DIR / "product_performance.csv"
    )

    category_performance = pd.read_csv(
        ANALYTICS_DIR / "category_performance.csv"
    )

    # ---------------------------------------------------------
    # 1. DAILY SALES
    # ---------------------------------------------------------

    assert daily_sales["order_date"].notna().all()
    assert daily_sales["order_date"].is_unique
    assert (daily_sales["orders"] > 0).all()
    assert (daily_sales["items_sold"] > 0).all()
    assert (daily_sales["revenue"] >= 0).all()

    # ---------------------------------------------------------
    # 2. CUSTOMER SALES
    # ---------------------------------------------------------

    assert customer_sales["customer_key"].notna().all()
    assert customer_sales["customer_key"].is_unique
    assert (customer_sales["orders"] > 0).all()
    assert (customer_sales["items_sold"] > 0).all()
    assert (customer_sales["revenue"] >= 0).all()

    # ---------------------------------------------------------
    # 3. PRODUCT PERFORMANCE
    # ---------------------------------------------------------

    assert product_performance["product_key"].notna().all()
    assert product_performance["product_key"].is_unique
    assert product_performance["product_name"].notna().all()
    assert product_performance["category"].notna().all()
    assert (product_performance["orders"] > 0).all()
    assert (product_performance["quantity_sold"] > 0).all()
    assert (product_performance["revenue"] >= 0).all()

    # ---------------------------------------------------------
    # 4. CATEGORY PERFORMANCE
    # ---------------------------------------------------------

    assert category_performance["category"].notna().all()
    assert category_performance["category"].is_unique
    assert (category_performance["orders"] > 0).all()
    assert (category_performance["quantity_sold"] > 0).all()
    assert (category_performance["revenue"] >= 0).all()

    # ---------------------------------------------------------
    # 5. REVENUE CONSISTENCY
    # ---------------------------------------------------------

    core_revenue = round(
        fact_order_item["sales_amount"].sum(),
        2,
    )

    analytics_revenue = round(
        daily_sales["revenue"].sum(),
        2,
    )

    assert core_revenue == analytics_revenue

    # ---------------------------------------------------------
    # 6. QUANTITY CONSISTENCY
    # ---------------------------------------------------------

    core_quantity = int(
        fact_order_item["quantity"].sum()
    )

    analytics_quantity = int(
        daily_sales["items_sold"].sum()
    )

    assert core_quantity == analytics_quantity

    print("DAILY_SALES validation: PASSED")
    print("CUSTOMER_SALES validation: PASSED")
    print("PRODUCT_PERFORMANCE validation: PASSED")
    print("CATEGORY_PERFORMANCE validation: PASSED")
    print("Revenue consistency validation: PASSED")
    print("Quantity consistency validation: PASSED")

    print("\nAll ANALYTICS data-quality checks PASSED!")


if __name__ == "__main__":
    main()