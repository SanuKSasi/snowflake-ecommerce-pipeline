
import os
from dotenv import load_dotenv
from snowflake.snowpark import Session

load_dotenv()


def get_snowpark_session():

    connection_parameters = {
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA")
    }

    session = Session.builder.configs(
        connection_parameters
    ).create()

    return session
