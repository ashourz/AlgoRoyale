import time

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from algo_royale.clients.db.database_manager import DatabaseManager
from algo_royale.clients.db.migrations.migration_manager import MigrationManager
from algo_royale.clients.db.process_manager import ProcessManager
from algo_royale.clients.db.user_manager import UserManager


class DatabaseAdmin:
    def __init__(
        self,
        master_db_name,
        master_db_user,
        master_db_password,
        db_host,
        db_port,
        logger,
    ):
        self.user_manager = UserManager(
            master_db_name, master_db_user, master_db_password, db_host, db_port, logger
        )
        self.process_manager = ProcessManager(logger=logger)
        self.database_manager = DatabaseManager(
            db_host=db_host, db_port=db_port, logger=logger
        )
        self.migration_manager = MigrationManager(logger=logger)
        self.db_host = db_host
        self.db_port = db_port
        self.logger = logger

    def setup_environment(
        self, db_name, db_user, db_password, service_name="postgresql-x64-13"
    ):
        if not self.process_manager.is_postgres_running(self.db_host, self.db_port):
            self.logger.info("Postgres service not running. Attempting to start...")
            started = self.process_manager.start_postgres_service(service_name)
            if not started:
                raise RuntimeError(
                    f"Could not start PostgreSQL service '{service_name}' on {self.db_host}:{self.db_port}"
                )
            self.logger.info("Postgres service started.")
        self.user_manager.create_user(username=db_user, password=db_password)
        self.database_manager.create_database(
            master_db_connection=self.get_master_db_connection(),
            db_name=db_name,
            create_if_not_exists=True,
        )
        self.run_migrations()
        self.user_manager.grant_privileges(db_name=db_name, username=db_user)

    def run_migrations(self, db_connection: psycopg2.extensions.connection):
        try:
            self.logger.info("🚀 Running database migrations...")
            self.migration_manager.apply_migrations(db_connection)
            db_connection.close()
        except Exception as e:
            self.logger.error(f"Error running migrations: {e}")
            raise e

    def get_master_db_connection(
        self,
        retries: int = 3,
        delay: int = 2,
    ):
        """
        Create a new database.
        """
        attempt = 0
        while attempt < retries:
            try:
                # Connect to the "postgres" database for creation if needed
                self.logger.info("🔗 Attempting to connect to the database...")
                conn = psycopg2.connect(
                    dbname=self.master_db_name,
                    user=self.master_db_user,
                    password=self.master_db_password,
                    host=self.db_host,
                    port=self.db_port,
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
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

    def get_db_connection(self, db_name: str, username: str, password: str):
        return self.database_manager.get_db_connection(
            db_name=db_name,
            username=username,
            password=password,
            create_if_not_exists=True,
        )

    def teardown_environment(self, service_name="postgresql-x64-13"):
        self.process_manager.unregister_instance()
        if not self.process_manager.any_other_instances_running():
            self.process_manager.stop_postgres_service(service_name)
