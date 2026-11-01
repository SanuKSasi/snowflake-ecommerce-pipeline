from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = PROJECT_ROOT / "data" / "core"


def main():
    print("Starting CORE data-quality validation...\n")

    dim_customer = pd.read_csv(
        CORE_DIR / "dim_customer.csv"
    )

    dim_product = pd.read_csv(
        CORE_DIR / "dim_product.csv"
    )

    fact_order = pd.read_csv(
        CORE_DIR / "fact_order.csv"
    )

    fact_order_item = pd.read_csv(
        CORE_DIR / "fact_order_item.csv"
    )

    # DIM_CUSTOMER
    assert dim_customer["customer_key"].notna().all()
    assert dim_customer["customer_key"].is_unique

    # DIM_PRODUCT
    assert dim_product["product_key"].notna().all()
    assert dim_product["product_key"].is_unique

    # FACT_ORDER
    assert fact_order["order_key"].notna().all()
    assert fact_order["order_key"].is_unique
    assert fact_order["order_id"].is_unique

    assert fact_order["customer_key"].isin(
        dim_customer["customer_key"]
    ).all()

    # FACT_ORDER_ITEM
    assert fact_order_item["order_item_key"].notna().all()
    assert fact_order_item["order_item_key"].is_unique

    assert fact_order_item["order_key"].isin(
        fact_order["order_key"]
    ).all()

    assert fact_order_item["product_key"].isin(
        dim_product["product_key"]
    ).all()

    # Sales amount validation
    expected_sales = (
        fact_order_item["quantity"]
        * fact_order_item["unit_price"]
    ).round(2)

    assert (
        fact_order_item["sales_amount"] == expected_sales
    ).all()

    print("DIM_CUSTOMER validation: PASSED")
    print("DIM_PRODUCT validation: PASSED")
    print("FACT_ORDER validation: PASSED")
    print("FACT_ORDER_ITEM validation: PASSED")
    print("Sales amount validation: PASSED")

    print("\nAll CORE data-quality checks PASSED!")


if __name__ == "__main__":
    main()