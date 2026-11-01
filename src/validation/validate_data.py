from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


def validate_customers(customers):
    assert customers["customer_id"].notna().all(), "Customer ID contains NULL values"
    assert customers["customer_id"].is_unique, "Duplicate customer IDs found"
    assert customers["email"].notna().all(), "Customer email contains NULL values"

    print("Customers validation: PASSED")


def validate_products(products):
    assert products["product_id"].notna().all(), "Product ID contains NULL values"
    assert products["product_id"].is_unique, "Duplicate product IDs found"
    assert (products["price"] > 0).all(), "Product price must be greater than 0"

    print("Products validation: PASSED")


def validate_orders(orders, customers):
    assert orders["order_id"].notna().all(), "Order ID contains NULL values"
    assert orders["order_id"].is_unique, "Duplicate order IDs found"

    valid_customers = set(customers["customer_id"])

    invalid_customers = set(orders["customer_id"]) - valid_customers

    assert not invalid_customers, (
        f"Orders contain unknown customer IDs: {invalid_customers}"
    )

    valid_statuses = {
        "COMPLETED",
        "CANCELLED",
        "RETURNED",
    }

    invalid_statuses = set(orders["status"]) - valid_statuses

    assert not invalid_statuses, (
        f"Invalid order statuses found: {invalid_statuses}"
    )

    print("Orders validation: PASSED")


def validate_order_items(order_items, orders, products):
    valid_orders = set(orders["order_id"])
    valid_products = set(products["product_id"])

    invalid_orders = set(order_items["order_id"]) - valid_orders
    invalid_products = set(order_items["product_id"]) - valid_products

    assert not invalid_orders, (
        f"Order items contain unknown order IDs: {invalid_orders}"
    )

    assert not invalid_products, (
        f"Order items contain unknown product IDs: {invalid_products}"
    )

    assert (order_items["quantity"] > 0).all(), (
        "Order quantity must be greater than 0"
    )

    assert (order_items["unit_price"] > 0).all(), (
        "Unit price must be greater than 0"
    )

    print("Order items validation: PASSED")


def main():
    customers = pd.read_csv(DATA_DIR / "customers.csv")
    products = pd.read_csv(DATA_DIR / "products.csv")
    orders = pd.read_csv(DATA_DIR / "orders.csv")
    order_items = pd.read_csv(DATA_DIR / "order_items.csv")

    print("\nStarting data-quality validation...\n")

    validate_customers(customers)
    validate_products(products)
    validate_orders(orders, customers)
    validate_order_items(order_items, orders, products)

    print("\nAll data-quality checks PASSED!")


if __name__ == "__main__":
    main()