# config/db_config.py

import time
import psycopg2
from config.config import DB_PARAMS, DB_SECRETS
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def get_db_connection(retries=3, delay=2, create_if_not_exists=False):
    """
    Create and return a psycopg2 database connection.
    Retry up to `retries` times if connection fails.
    
    If `create_if_not_exists` is True, it will attempt to create the database if it doesn't exist.
    """
    dbname = DB_PARAMS["dbname"]
    user = DB_PARAMS["user"]
    password = DB_SECRETS["password"]
    host = DB_PARAMS["host"]
    port = int(DB_PARAMS["port"])

    attempt = 0
    while attempt < retries:
        try:
            # Create the connection to "postgres" database for DB creation if needed
            conn = psycopg2.connect(
                dbname="postgres",  # Connecting to the default "postgres" database to create the target one
                user=user,
                password=password,
                host=host,
                port=port,
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            if create_if_not_exists:
                # Check if the target database exists; create if it doesn't
                with conn.cursor() as cur:
                    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
                    if not cur.fetchone():
                        cur.execute(f"CREATE DATABASE {dbname}")
                        print(f"✅ Created database: {dbname}")
                    else:
                        print(f"ℹ️ Database already exists: {dbname}")

            return conn  # Return the connection, regardless of whether it's the creation connection or the target DB connection

        except psycopg2.OperationalError as e:
            attempt += 1
            print(f"⚠️  Database connection failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(delay)  # wait before retrying
            else:
                print("❌ Max retries reached. Could not connect to the database.")
                raise

def close_connection(conn):
    """
    Closes the database connection.
    """
    if conn:
        conn.close()
        print("✅ Connection closed.")
