# config/db_config.py

import time
import psycopg2
from config.config import DB_PARAMS, DB_SECRETS

def get_db_connection(retries=3, delay=2):
    """
    Create and return a psycopg2 database connection.
    Retry up to `retries` times if connection fails.
    """
    attempt = 0
    while attempt < retries:
        try:
            conn = psycopg2.connect(
                dbname=DB_PARAMS["dbname"],
                user=DB_PARAMS["user"],
                password=DB_SECRETS["password"],
                host=DB_PARAMS["host"],
                port=int(DB_PARAMS["port"]),
            )
            print(f"✅ Connected to database on attempt {attempt + 1}")
            return conn
        except psycopg2.OperationalError as e:
            attempt += 1
            print(f"⚠️  Database connection failed (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(delay)  # wait before retrying
            else:
                print("❌ Max retries reached. Could not connect to the database.")
                raise

