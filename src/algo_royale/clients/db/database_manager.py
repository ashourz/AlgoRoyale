import time

import psycopg2


class DatabaseManager:
    def __init__(
        self,
        db_host,
        db_port,
        logger,
    ):
        self.db_host = db_host
        self.db_port = db_port
        self.logger = logger

    def create_database(
        self,
        master_db_connection: psycopg2.extensions.connection,
        db_name: str,
        retries: int = 3,
        delay: int = 2,
        create_if_not_exists: bool = False,
    ):
        """
        Create a new database.
        """
        attempt = 0
        while attempt < retries:
            try:
                self.logger.info("✅ Connected to the master database.")
                if create_if_not_exists:
                    self.logger.info(f"🛠️ Ensuring database '{db_name}' exists...")
                    # Check if the target database exists; create it if it doesn't
                    with master_db_connection.cursor() as cur:
                        cur.execute(
                            f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
                        )
                        if not cur.fetchone():
                            self.logger.info(f"🛠️ Creating database: {db_name}")
                            cur.execute(f"CREATE DATABASE {db_name}")
                            self.logger.info(f"✅ Created database: {db_name}")
                        else:
                            self.logger.info(f"ℹ️ Database already exists: {db_name}")
            except psycopg2.OperationalError as e:
                attempt += 1
                self.logger.error(
                    f"⚠️ Database creation failed (attempt {attempt}/{retries}): {e}"
                )
                if attempt < retries:
                    time.sleep(delay)
                else:
                    self.logger.error(
                        "❌ Max retries reached. Could not complete database creation."
                    )
                    raise

    def get_db_connection(
        self,
        db_name: str,
        username: str,
        password: str,
        retries: int = 3,
        delay: int = 2,
        create_if_not_exists: bool = False,
    ) -> psycopg2.extensions.connection:
        """
        Establish a connection to the database. Optionally create the database if it doesn't exist.
        """
        attempt = 0
        while attempt < retries:
            try:
                # Connect to the target database
                self.logger.info("🔗 Connecting to the target database...")
                self.connection = psycopg2.connect(
                    dbname=db_name,
                    user=username,
                    password=password,
                    host=self.db_host,
                    port=self.db_port,
                )
                self.logger.info("✅ Target database connection established.")
                return self.connection

            except psycopg2.OperationalError as e:
                attempt += 1
                self.logger.error(
                    f"⚠️ Database connection failed (attempt {attempt}/{retries}): {e}"
                )
                if attempt < retries:
                    time.sleep(delay)
                else:
                    self.logger.error(
                        "❌ Max retries reached. Could not connect to the database."
                    )
                    raise
