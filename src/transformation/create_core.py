from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STAGING_DIR = PROJECT_ROOT / "data" / "staging"
CORE_DIR = PROJECT_ROOT / "data" / "core"

CORE_DIR.mkdir(exist_ok=True)


def create_dim_customer():
    customers = pd.read_csv(
        STAGING_DIR / "customers.csv",
        parse_dates=["signup_date"],
    )

    customers.insert(
        0,
        "customer_key",
        range(1, len(customers) + 1),
    )

    return customers[
        [
            "customer_key",
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "city",
            "signup_date",
        ]
    ]


def create_dim_product():
    products = pd.read_csv(STAGING_DIR / "products.csv")

    products.insert(
        0,
        "product_key",
        range(1, len(products) + 1),
    )

    return products[
        [
            "product_key",
            "product_id",
            "product_name",
            "category",
            "price",
        ]
    ]


def create_fact_order(orders, dim_customer):
    fact_order = orders.merge(
        dim_customer[
            ["customer_key", "customer_id"]
        ],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    fact_order.insert(
        0,
        "order_key",
        range(1, len(fact_order) + 1),
    )

    return fact_order[
        [
            "order_key",
            "order_id",
            "customer_key",
            "order_date",
            "status",
        ]
    ]


def create_fact_order_item(
    order_items,
    fact_order,
    dim_product,
):
    fact_order_item = order_items.merge(
        fact_order[
            ["order_key", "order_id"]
        ],
        on="order_id",
        how="left",
        validate="many_to_one",
    )

    fact_order_item = fact_order_item.merge(
        dim_product[
            ["product_key", "product_id"]
        ],
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    fact_order_item["sales_amount"] = (
        fact_order_item["quantity"]
        * fact_order_item["unit_price"]
    ).round(2)

    fact_order_item.insert(
        0,
        "order_item_key",
        range(1, len(fact_order_item) + 1),
    )

    return fact_order_item[
        [
            "order_item_key",
            "order_key",
            "product_key",
            "quantity",
            "unit_price",
            "sales_amount",
        ]
    ]


def main():
    print("Creating CORE data model...\n")

    # Read STAGING data
    customers = pd.read_csv(
        STAGING_DIR / "customers.csv",
        parse_dates=["signup_date"],
    )

    products = pd.read_csv(
        STAGING_DIR / "products.csv"
    )

    orders = pd.read_csv(
        STAGING_DIR / "orders.csv",
        parse_dates=["order_date"],
    )

    order_items = pd.read_csv(
        STAGING_DIR / "order_items.csv"
    )

    # Create dimensions
    dim_customer = create_dim_customer()
    dim_product = create_dim_product()

    # Create facts
    fact_order = create_fact_order(
        orders,
        dim_customer,
    )

    fact_order_item = create_fact_order_item(
        order_items,
        fact_order,
        dim_product,
    )

    # Write CORE tables
    dim_customer.to_csv(
        CORE_DIR / "dim_customer.csv",
        index=False,
    )

    dim_product.to_csv(
        CORE_DIR / "dim_product.csv",
        index=False,
    )

    fact_order.to_csv(
        CORE_DIR / "fact_order.csv",
        index=False,
    )

    fact_order_item.to_csv(
        CORE_DIR / "fact_order_item.csv",
        index=False,
    )

    print("CORE transformation completed.\n")

    print(f"DIM_CUSTOMER    : {len(dim_customer):,}")
    print(f"DIM_PRODUCT     : {len(dim_product):,}")
    print(f"FACT_ORDER      : {len(fact_order):,}")
    print(f"FACT_ORDER_ITEM : {len(fact_order_item):,}")


if __name__ == "__main__":
    main()