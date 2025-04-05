import psycopg2
from config.config import DB_PARAMS  # Import DB credentials
from contextlib import contextmanager  # For context manager support


@contextmanager
def connect_db():
    """Context manager for connecting to PostgreSQL."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        print("✅ Database connection established.")
        yield conn  # Yield the connection object to the caller
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        raise  # Reraise the exception to propagate it
    finally:
        if conn:
            conn.close()  # Ensure connection is closed after use
            print("✅ Database connection closed.")


def close_db(conn):
    """Close the database connection."""
    try:
        if conn:
            conn.close()
            print("✅ Database connection closed.")
    except Exception as e:
        print(f"❌ Error closing the database connection: {e}")
        raise
