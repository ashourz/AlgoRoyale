from logging import Logger
import time
from contextlib import contextmanager
from typing import Generator
from algo_royale.config.config import Config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from algo_royale.logging.logger_singleton import Environment, LoggerSingleton, LoggerType

class Database:
    def __init__(self, logger: Logger, config: Config, secrets: Config):
        self.logger = logger
        self.db_params = config.get_section("db.connection")
        self.db_secrets = secrets.get_section("db.connection")
        self.connection = None

    def connect(self, retries=3, delay=2, create_if_not_exists=False) -> psycopg2.extensions.connection:
        """
        Establish a connection to the database. Optionally create the database if it doesn't exist.
        """
        dbname = self.db_params["dbname"]
        user = self.db_params["user"]
        password = self.db_secrets["password"]
        host = self.db_params["host"]
        port = int(self.db_params["port"])

        attempt = 0
        while attempt < retries:
            try:
                # Connect to the "postgres" database for creation if needed
                conn = psycopg2.connect(
                    dbname="postgres",
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

                if create_if_not_exists:
                    # Check if the target database exists; create it if it doesn't
                    with conn.cursor() as cur:
                        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
                        if not cur.fetchone():
                            cur.execute(f"CREATE DATABASE {dbname}")
                            self.logger.info(f"✅ Created database: {dbname}")
                        else:
                            self.logger.info(f"ℹ️ Database already exists: {dbname}")

                # Connect to the target database
                self.connection = psycopg2.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                )
                self.logger.info("✅ Database connection established.")
                return self.connection

            except psycopg2.OperationalError as e:
                attempt += 1
                self.logger.error(f"⚠️ Database connection failed (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    time.sleep(delay)
                else:
                    self.logger.error("❌ Max retries reached. Could not connect to the database.")
                    raise

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.logger.info("✅ Database connection closed.")

    @contextmanager
    def connection_context(self, create_if_not_exists=False) -> Generator[psycopg2.extensions.connection, None, None]:
        """
        Context manager for database connections.
        """
        try:
            conn = self.connect(create_if_not_exists=create_if_not_exists)
            yield conn
        except Exception as e:
            self.logger.error(f"❌ Error during database operation: {e}")
            raise
        finally:
            self.close()