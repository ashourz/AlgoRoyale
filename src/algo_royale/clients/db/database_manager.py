import time

import psycopg2
from psycopg2 import sql

from algo_royale.clients.db.db_utils import is_valid_identifier


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
        # Validate database name
        if not is_valid_identifier(db_name):
            raise ValueError(f"Invalid database name: {db_name}")

        attempt = 0
        while attempt < retries:
            try:
                self.logger.info("✅ Connected to the master database.")
                if create_if_not_exists:
                    self.logger.info(f"🛠️ Ensuring database '{db_name}' exists...")
                    # Check if the target database exists; create it if it doesn't
                    with master_db_connection.cursor() as cur:
                        # Parameterize the datname check to avoid injection
                        cur.execute(
                            "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
                        )
                        if not cur.fetchone():
                            self.logger.info(f"🛠️ Creating database: {db_name}")
                            # Use Identifier for the database name
                            cur.execute(
                                sql.SQL("CREATE DATABASE {};").format(
                                    sql.Identifier(db_name)
                                )
                            )
                            self.logger.info(f"✅ Created database: {db_name}")
                        else:
                            self.logger.info(f"ℹ️ Database already exists: {db_name}")
                break

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

    def drop_database(
        self,
        master_db_connection: psycopg2.extensions.connection,
        db_name: str,
    ):
        """
        Drop an existing database.
        """
        # Validate database name
        if not is_valid_identifier(db_name):
            raise ValueError(f"Invalid database name: {db_name}")

        try:
            self.logger.info(f"🛠️ Dropping database '{db_name}' if exists...")
            master_db_connection.set_isolation_level(
                psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
            )
            with master_db_connection.cursor() as cur:
                # Terminate all connections to the target database (parameterized)
                cur.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s AND pid <> pg_backend_pid();",
                    (db_name,),
                )
                # Drop the target database using an Identifier
                cur.execute(
                    sql.SQL("DROP DATABASE IF EXISTS {};").format(
                        sql.Identifier(db_name)
                    )
                )
                self.logger.info(f"✅ Dropped database: {db_name}")
        except Exception as e:
            self.logger.error(f"❌ Error dropping database '{db_name}': {e}")
            raise

    def drop_table(
        self, master_db_connection: psycopg2.extensions.connection, table_name: str
    ):
        if not is_valid_identifier(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        try:
            self.logger.info(f"Dropping table '{table_name}'...")
            with master_db_connection.cursor() as cur:
                cur.execute(
                    sql.SQL("DROP TABLE IF EXISTS {} CASCADE;").format(
                        sql.Identifier(table_name)
                    )
                )
                master_db_connection.commit()
            self.logger.info(f"Table '{table_name}' dropped successfully.")
        except Exception as e:
            self.logger.error(f"Error dropping table '{table_name}': {e}")
            raise

    def drop_all_tables(self, master_db_connection: psycopg2.extensions.connection):
        """
        Drop all tables in the connected database. Use with caution!
        """
        try:
            self.logger.info("🧹 Dropping all tables in the database...")
            with master_db_connection.cursor() as cur:
                drop_tables_query = """
                DO $$ DECLARE
                    r RECORD;
                BEGIN
                    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                    END LOOP;
                END $$;
                """
                cur.execute(drop_tables_query)
                master_db_connection.commit()
                self.logger.info("✅ All tables dropped successfully.")
        except Exception as e:
            self.logger.error(f"❌ Error dropping all tables: {e}")
            raise
