from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
STAGING_DIR = DATA_DIR / "staging"

STAGING_DIR.mkdir(exist_ok=True)


def transform_customers():
    customers = pd.read_csv(
        DATA_DIR / "customers.csv",
        parse_dates=["signup_date"],
    )

    customers["first_name"] = customers["first_name"].str.strip()
    customers["last_name"] = customers["last_name"].str.strip()
    customers["email"] = customers["email"].str.strip().str.lower()
    customers["city"] = customers["city"].str.strip()

    return customers


def transform_products():
    products = pd.read_csv(DATA_DIR / "products.csv")

    products["product_name"] = products["product_name"].str.strip()
    products["category"] = products["category"].str.strip()
    products["price"] = products["price"].astype(float)

    return products


def transform_orders():
    orders = pd.read_csv(
        DATA_DIR / "orders.csv",
        parse_dates=["order_date"],
    )

    orders["status"] = orders["status"].str.strip().str.upper()

    return orders


def transform_order_items():
    order_items = pd.read_csv(DATA_DIR / "order_items.csv")

    order_items["quantity"] = order_items["quantity"].astype(int)
    order_items["unit_price"] = order_items["unit_price"].astype(float)

    return order_items


def main():
    print("Creating STAGING datasets...\n")

    customers = transform_customers()
    products = transform_products()
    orders = transform_orders()
    order_items = transform_order_items()

    customers.to_csv(
        STAGING_DIR / "customers.csv",
        index=False,
    )

    products.to_csv(
        STAGING_DIR / "products.csv",
        index=False,
    )

    orders.to_csv(
        STAGING_DIR / "orders.csv",
        index=False,
    )

    order_items.to_csv(
        STAGING_DIR / "order_items.csv",
        index=False,
    )

    print("STAGING transformation completed.")
    print(f"Customers   : {len(customers):,}")
    print(f"Products    : {len(products):,}")
    print(f"Orders      : {len(orders):,}")
    print(f"Order Items : {len(order_items):,}")


if __name__ == "__main__":
    main()