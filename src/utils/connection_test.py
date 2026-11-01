import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()
conn=snowflake.connector.connect(
account=os.getenv("SNOWFLAKE_ACCOUNT"),
user=os.getenv("SNOWFLAKE_USER"),
password=os.getenv("SNOWFLAKE_PASSWORD"),
warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
database=os.getenv("SNOWFLAKE_DATABASE"),
schema=os.getenv("SNOWFLAKE_SCHEMA"))

cursor=conn.cursor()

try:
    cursor.execute("""SELECT CURRENT_USER(),CURRENT_ROLE(),CURRENT_DATABASE(),CURRENT_WAREHOSHOUSE()""")
    result=cursor.fetchone()
    print("snowflake connection is successful")
    print(f"User: {result[0]}")
    print(f"Role: {result[1]}")
    print(f"Database: {result[2]}")
    print(f"Warehouse: {result[3]}")
    
finally:
    cursor.close()
    conn.close()