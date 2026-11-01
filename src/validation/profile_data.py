from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"


FILES = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "order_items.csv",
]


def profile_file(file_name: str) -> None:
    file_path = DATA_DIR / file_name

    df = pd.read_csv(file_path)

    print("\n" + "=" * 60)
    print(f"FILE: {file_name}")
    print("=" * 60)

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")

    print("\nColumns:")
    print(list(df.columns))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    print("\nData types:")
    print(df.dtypes)

    print("\nSample:")
    print(df.head(3))


def main():
    for file_name in FILES:
        profile_file(file_name)


if __name__ == "__main__":
    main()