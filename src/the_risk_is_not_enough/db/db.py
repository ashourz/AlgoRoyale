import psycopg2
from config.db_config import get_db_connection, close_connection  # Import the new centralized connection function
from contextlib import contextmanager

from logger.logger_singleton import Environment, LoggerSingleton, LoggerType


logger = LoggerSingleton(LoggerType.TRADING, Environment.PRODUCTION).get_logger()

@contextmanager
def connect_db(create_if_not_exists=False):
    """Context manager for connecting to PostgreSQL."""
    conn = None
    try:
        # Use get_db_connection to handle connection and database creation
        conn = get_db_connection(create_if_not_exists=create_if_not_exists)
        logger.info("✅ Database connection established.")
        yield conn  # Yield the connection object to the caller
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {e}")
        raise  # Reraise the exception to propagate it
    finally:
        if conn:
            close_connection(conn)  # Ensure connection is closed after use


def close_db(conn):
    """Close the database connection."""
    try:
        close_connection(conn)  # Close connection via the centralized function
        logger.info("✅ Database connection closed.")
    except Exception as e:
        logger.error(f"❌ Error closing the database connection: {e}")
        raise
