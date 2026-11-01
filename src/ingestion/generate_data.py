from pathlib import Path
from datetime import datetime, timedelta
import random

import pandas as pd


# --------------------------------------------------
# Configuration
# --------------------------------------------------

RANDOM_SEED = 42
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 200
NUM_ORDERS = 5000

random.seed(RANDOM_SEED)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)


# --------------------------------------------------
# Reference data
# --------------------------------------------------

FIRST_NAMES = [
    "Arun", "Rahul", "Akhil", "Vishnu", "Aditya",
    "Anu", "Meera", "Neha", "Priya", "Sneha",
    "Asha", "Divya", "Kiran", "Nikhil", "Riya"
]

LAST_NAMES = [
    "Kumar", "Nair", "Menon", "Sharma", "Thomas",
    "Joseph", "Varma", "Reddy", "Pillai", "Iyer"
]

CITIES = [
    "Kochi", "Bangalore", "Chennai", "Hyderabad",
    "Mumbai", "Delhi", "Pune", "Coimbatore",
    "Trivandrum", "Thrissur", "Kozhikode", "Palakkad"
]

CATEGORIES = {
    "Electronics": ["Laptop", "Mobile", "Tablet", "Headphones", "Monitor"],
    "Home": ["Chair", "Table", "Lamp", "Mixer", "Vacuum Cleaner"],
    "Fashion": ["Shirt", "Jeans", "Shoes", "Jacket", "Backpack"],
    "Sports": ["Football", "Badminton Racket", "Yoga Mat", "Cricket Bat"],
    "Books": ["Fiction Book", "Technology Book", "Business Book", "Cookbook"],
}


# --------------------------------------------------
# Generate customers
# --------------------------------------------------

def generate_customers():
    rows = []

    start_date = datetime(2024, 1, 1)

    for customer_id in range(1, NUM_CUSTOMERS + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        signup_date = start_date + timedelta(
            days=random.randint(0, 900)
        )

        rows.append({
            "customer_id": f"C{customer_id:05d}",
            "first_name": first_name,
            "last_name": last_name,
            "email": f"{first_name.lower()}.{last_name.lower()}{customer_id}@example.com",
            "city": random.choice(CITIES),
            "signup_date": signup_date.date(),
        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# Generate products
# --------------------------------------------------

def generate_products():
    rows = []

    product_id = 1
    product_types = [
        (category, product_type)
        for category, products in CATEGORIES.items()
        for product_type in products
    ]

    for _ in range(NUM_PRODUCTS):
        category, product_type = random.choice(product_types)

        rows.append({
            "product_id": f"P{product_id:05d}",
            "product_name": product_type,
            "category": category,
            "price": round(random.uniform(500, 75000), 2),
        })

        product_id += 1

    return pd.DataFrame(rows)


# --------------------------------------------------
# Generate orders and order items
# --------------------------------------------------

def generate_orders(customers, products):
    order_rows = []
    item_rows = []

    start_date = datetime(2025, 1, 1)

    statuses = [
        "COMPLETED",
        "COMPLETED",
        "COMPLETED",
        "CANCELLED",
        "RETURNED",
    ]

    for order_id in range(1, NUM_ORDERS + 1):

        customer_id = random.choice(customers["customer_id"].tolist())

        order_date = start_date + timedelta(
            days=random.randint(0, 630)
        )

        status = random.choice(statuses)

        order_rows.append({
            "order_id": f"O{order_id:06d}",
            "customer_id": customer_id,
            "order_date": order_date.date(),
            "status": status,
        })

        # Each order contains 1–4 products
        number_of_items = random.randint(1, 4)

        selected_products = products.sample(
            n=number_of_items,
            random_state=random.randint(1, 100000)
        )

        for _, product in selected_products.iterrows():

            quantity = random.randint(1, 4)

            item_rows.append({
                "order_id": f"O{order_id:06d}",
                "product_id": product["product_id"],
                "quantity": quantity,
                "unit_price": product["price"],
            })

    return pd.DataFrame(order_rows), pd.DataFrame(item_rows)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("Generating customers...")
    customers = generate_customers()

    print("Generating products...")
    products = generate_products()

    print("Generating orders...")
    orders, order_items = generate_orders(customers, products)

    customers.to_csv(DATA_DIR / "customers.csv", index=False)
    products.to_csv(DATA_DIR / "products.csv", index=False)
    orders.to_csv(DATA_DIR / "orders.csv", index=False)
    order_items.to_csv(DATA_DIR / "order_items.csv", index=False)

    print("\nData generation completed!")
    print(f"Customers    : {len(customers):,}")
    print(f"Products     : {len(products):,}")
    print(f"Orders       : {len(orders):,}")
    print(f"Order Items  : {len(order_items):,}")

    print(f"\nFiles created in: {DATA_DIR}")


if __name__ == "__main__":
    main()