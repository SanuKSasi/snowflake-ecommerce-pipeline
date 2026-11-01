
from pathlib import Path

from src.utils.snowflake_connection import get_snowflake_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

FILES = {
    "customers.csv": "CUSTOMERS",
    "products.csv": "PRODUCTS",
    "orders.csv": "ORDERS",
    "order_items.csv": "ORDER_ITEMS"
}


def load_csv_files():
    connection = None

    try:
        connection = get_snowflake_connection()

        with connection.cursor() as cursor:

            cursor.execute("""
                CREATE STAGE IF NOT EXISTS RAW.ECOMMERCE_STAGE
            """)

            print("Snowflake stage is ready.")

            for file_name, table_name in FILES.items():

                file_path = DATA_DIR / file_name

                if not file_path.exists():
                    raise FileNotFoundError(file_path)

                temp_table = f"TMP_LOAD_{table_name}"

                # Create a temporary table matching the RAW table
                cursor.execute(
                    f"CREATE OR REPLACE TEMP TABLE {temp_table} "
                    f"LIKE RAW.{table_name}"
                )

                # Upload local CSV to Snowflake internal stage
                put_command = (
                    f"PUT 'file://{file_path.as_posix()}' "
                    f"@RAW.ECOMMERCE_STAGE "
                    "AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
                )

                cursor.execute(put_command)
                print(f"Uploaded: {file_name}")

                # Load CSV into temporary table
                copy_command = f"""
                    COPY INTO {temp_table}
                    FROM @RAW.ECOMMERCE_STAGE/{file_name}.gz
                    FILE_FORMAT = (
                        TYPE = CSV
                        SKIP_HEADER = 1
                        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                    )
                    ON_ERROR = 'ABORT_STATEMENT'
                """

                cursor.execute(copy_command)
                copy_results = cursor.fetchall()

                loaded_rows = sum(
                    result[3] for result in copy_results
                )

                if loaded_rows == 0:
                    raise RuntimeError(
                        f"No records loaded from {file_name}"
                    )

                # Verify temporary table record count
                cursor.execute(
                    f"SELECT COUNT(*) FROM {temp_table}"
                )
                temp_count = cursor.fetchone()[0]

                if temp_count != loaded_rows:
                    raise RuntimeError(
                        f"Row count mismatch for {table_name}"
                    )

                # Replace RAW data transactionally
                try:
                    cursor.execute("BEGIN TRANSACTION")

                    cursor.execute(
                        f"DELETE FROM RAW.{table_name}"
                    )

                    cursor.execute(
                        f"""
                        INSERT INTO RAW.{table_name}
                        SELECT * FROM {temp_table}
                        """
                    )

                    cursor.execute("COMMIT")

                except Exception:
                    cursor.execute("ROLLBACK")
                    raise

                print(
                    f"{table_name}: {temp_count} records loaded "
                    "and verified."
                )

        print("\nAll four RAW tables refreshed successfully.")

    except Exception as error:
        print("\nIngestion failed:", error)
        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    load_csv_files()
