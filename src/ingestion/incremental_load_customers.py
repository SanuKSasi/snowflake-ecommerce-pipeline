
from pathlib import Path

from src.utils.snowflake_connection import get_snowflake_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CUSTOMER_FILE = PROJECT_ROOT / "data" / "customers.csv"

STAGE_NAME = "RAW.ECOMMERCE_STAGE"
TARGET_TABLE = "RAW.CUSTOMERS"
TEMP_TABLE = "TMP_CUSTOMER_INCREMENTAL"


def incremental_load_customers():

    connection = None

    try:
        connection = get_snowflake_connection()

        with connection.cursor() as cursor:

            if not CUSTOMER_FILE.exists():
                raise FileNotFoundError(CUSTOMER_FILE)

            print("Starting incremental customer ingestion...")

            # 1. Ensure internal stage exists
            cursor.execute(
                f"CREATE STAGE IF NOT EXISTS {STAGE_NAME}"
            )

            # 2. Create temporary staging table
            cursor.execute(
                f"""
                CREATE OR REPLACE TEMP TABLE {TEMP_TABLE}
                LIKE {TARGET_TABLE}
                """
            )

            # 3. Upload customer CSV
            put_command = (
                f"PUT 'file://{CUSTOMER_FILE.as_posix()}' "
                f"@{STAGE_NAME} "
                "AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
            )

            cursor.execute(put_command)

            print("Customer CSV uploaded successfully.")

            # 4. Load CSV into temporary table
            copy_command = f"""
                COPY INTO {TEMP_TABLE}
                FROM @{STAGE_NAME}/customers.csv.gz
                FILE_FORMAT = (
                    TYPE = CSV
                    SKIP_HEADER = 1
                    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                )
                FORCE = TRUE
                ON_ERROR = 'ABORT_STATEMENT'
            """

            cursor.execute(copy_command)
            copy_results = cursor.fetchall()

            loaded_rows = sum(
                result[3] for result in copy_results
            )

            # 5. Validate source data
            cursor.execute(
                f"""
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT CUSTOMER_ID)
                FROM {TEMP_TABLE}
                """
            )

            total_rows, unique_ids = cursor.fetchone()

            if total_rows != loaded_rows:
                raise RuntimeError("CSV row count mismatch.")

            if total_rows != unique_ids:
                raise RuntimeError(
                    "Duplicate CUSTOMER_ID values found."
                )

            print(f"Source records validated: {total_rows}")

            # 6. Perform incremental MERGE
            merge_sql = f"""
                MERGE INTO {TARGET_TABLE} T
                USING {TEMP_TABLE} S
                    ON T.CUSTOMER_ID = S.CUSTOMER_ID

                WHEN MATCHED AND (
                       T.FIRST_NAME IS DISTINCT FROM S.FIRST_NAME
                    OR T.LAST_NAME IS DISTINCT FROM S.LAST_NAME
                    OR T.EMAIL IS DISTINCT FROM S.EMAIL
                    OR T.CITY IS DISTINCT FROM S.CITY
                    OR T.SIGNUP_DATE IS DISTINCT FROM S.SIGNUP_DATE
                )
                THEN UPDATE SET
                    T.FIRST_NAME = S.FIRST_NAME,
                    T.LAST_NAME = S.LAST_NAME,
                    T.EMAIL = S.EMAIL,
                    T.CITY = S.CITY,
                    T.SIGNUP_DATE = S.SIGNUP_DATE

                WHEN NOT MATCHED THEN INSERT (
                    CUSTOMER_ID,
                    FIRST_NAME,
                    LAST_NAME,
                    EMAIL,
                    CITY,
                    SIGNUP_DATE
                )
                VALUES (
                    S.CUSTOMER_ID,
                    S.FIRST_NAME,
                    S.LAST_NAME,
                    S.EMAIL,
                    S.CITY,
                    S.SIGNUP_DATE
                )
            """

            cursor.execute(merge_sql)

            merge_result = cursor.fetchone()

            inserted = merge_result[0]
            updated = merge_result[1]

            print("\nIncremental loading completed.")
            print(f"Records inserted : {inserted}")
            print(f"Records updated  : {updated}")

            # 7. Verify target uniqueness
            cursor.execute(
                f"""
                SELECT
                    COUNT(*),
                    COUNT(DISTINCT CUSTOMER_ID)
                FROM {TARGET_TABLE}
                """
            )

            total, unique = cursor.fetchone()

            if total != unique:
                raise RuntimeError(
                    "Target contains duplicate customer IDs."
                )

            print(f"Target customer count: {total}")
            print("Target uniqueness validation: PASSED")

    except Exception as error:
        print("\nIncremental loading failed:", error)
        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    incremental_load_customers()
