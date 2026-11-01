
from src.utils.snowflake_connection import get_snowflake_connection

connection = None

try:
    connection = get_snowflake_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            CURRENT_ACCOUNT(),
            CURRENT_USER(),
            CURRENT_WAREHOUSE(),
            CURRENT_DATABASE(),
            CURRENT_SCHEMA()
    """)

    result = cursor.fetchone()

    print("Snowflake connection successful!")
    print("Account   :", result[0])
    print("User      :", result[1])
    print("Warehouse :", result[2])
    print("Database  :", result[3])
    print("Schema    :", result[4])

except Exception as error:
    print("Snowflake connection failed.")
    print("Error:", error)

finally:
    if connection:
        connection.close()
