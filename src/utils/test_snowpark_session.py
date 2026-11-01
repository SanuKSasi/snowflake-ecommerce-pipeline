
from src.utils.snowpark_session import get_snowpark_session

session = None

try:
    session = get_snowpark_session()

    print("Snowpark session created successfully!")

    print("Current database:", session.get_current_database())
    print("Current schema:", session.get_current_schema())
    print("Current warehouse:", session.get_current_warehouse())

    customers = session.table("RAW.CUSTOMERS")

    print("Customer count:", customers.count())

except Exception as error:
    print("Snowpark session failed:", error)
    raise

finally:
    if session:
        session.close()
