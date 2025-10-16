import time

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from algo_royale.clients.db.database_manager import DatabaseManager
from algo_royale.clients.db.db_utils import is_valid_identifier
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
        self.master_db_name = master_db_name
        self.master_db_user = master_db_user
        self.master_db_password = master_db_password
        self.user_manager = UserManager(logger=logger)
        self.process_manager = ProcessManager(logger=logger)
        self.database_manager = DatabaseManager(
            db_host=db_host, db_port=db_port, logger=logger
        )
        self.migration_manager = MigrationManager(logger=logger)
        self.db_host = db_host
        self.db_port = db_port
        self.logger = logger

    def setup_environment(
        self, db_name, db_user, db_password, service_name="postgresql-x64-18"
    ):
        self.logger.debug(
            "[setup_environment] Checking if Postgres service is running..."
        )
        if not self.process_manager.is_postgres_running(self.db_host, self.db_port):
            self.logger.info("Postgres service not running. Attempting to start...")
            started = self.process_manager.start_postgres_service(service_name)
            if not started:
                raise RuntimeError(
                    f"Could not start PostgreSQL service '{service_name}' on {self.db_host}:{self.db_port}"
                )
            self.logger.info("Postgres service started.")
        self.logger.info("✅ PostgreSQL service is running.")
        self.logger.debug("[setup_environment] Getting master DB connection...")
        master_db_connection = self.get_master_db_connection()
        self.logger.debug("[setup_environment] Creating or updating user...")
        self.user_manager.create_user(
            master_db_connection=master_db_connection,
            username=db_user,
            password=db_password,
        )
        self.logger.info("✅ User created.")
        self.logger.debug("[setup_environment] Creating database if not exists...")
        self.database_manager.create_database(
            master_db_connection=master_db_connection,
            db_name=db_name,
            create_if_not_exists=True,
        )
        self.logger.info("✅ Database created.")
        self.logger.debug("[setup_environment] Running migrations as master user...")
        # Run migrations as master user (admin)
        self.run_migrations(
            db_connection=self.get_db_connection(
                db_name=db_name,
                username=self.master_db_user,
                password=self.master_db_password,
            )
        )
        self.logger.info("✅ Migrations completed.")
        self.logger.debug("[setup_environment] Granting privileges to test user...")
        # get master connection to target db
        target_db_connection = self.get_db_connection(
            db_name=db_name,
            username=self.master_db_user,
            password=self.master_db_password,
        )
        target_db_connection.autocommit = True
        self.user_manager.grant_privileges(
            master_db_connection=master_db_connection,
            target_db_connection=target_db_connection,
            db_name=db_name,
            username=db_user,
        )
        self.logger.info("✅ Privileges granted.")
        master_db_connection.close()
        target_db_connection.close()
        self.logger.info("✅ Database environment setup complete.")

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
        db_name: str = None,
    ) -> psycopg2.extensions.connection:
        """
        Create a new database.
        """
        db_name = db_name or self.master_db_name
        if not is_valid_identifier(db_name):
            raise ValueError(f"Invalid database name: {db_name}")
        attempt = 0
        while attempt < retries:
            try:
                # Connect to the "postgres" database for creation if needed
                self.logger.info("🔗 Attempting to connect to the database...")
                conn = psycopg2.connect(
                    dbname=db_name,
                    user=self.master_db_user,
                    password=self.master_db_password,
                    host=self.db_host,
                    port=self.db_port,
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                return conn
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

    def drop_database(self, db_name: str):
        try:
            master_db_connection = self.get_master_db_connection()
            self.database_manager.drop_database(
                master_db_connection=master_db_connection,
                db_name=db_name,
            )
        except Exception as e:
            self.logger.error(f"Error dropping database {db_name}: {e}")
            raise e
        finally:
            master_db_connection.close()

    def drop_user(self, username: str):
        try:
            master_db_connection = self.get_master_db_connection()
            self.user_manager.delete_user(
                master_db_connection=master_db_connection,
                username=username,
            )
        except Exception as e:
            self.logger.error(f"Error dropping user {username}: {e}")
            raise e
        finally:
            master_db_connection.close()

    def drop_all_tables(self, db_name: str):
        try:
            master_db_connection = self.get_master_db_connection(db_name=db_name)
            self.database_manager.drop_all_tables(
                master_db_connection=master_db_connection
            )
        except Exception as e:
            self.logger.error(f"Error dropping all tables: {e}")
            raise e
        finally:
            master_db_connection.close()

    def drop_table(self, db_name: str, table_name: str):
        try:
            master_db_connection = self.get_master_db_connection(db_name=db_name)
            self.database_manager.drop_table(
                master_db_connection=master_db_connection,
                table_name=table_name,
            )
        except Exception as e:
            self.logger.error(f"Error dropping table {table_name}: {e}")
            raise e
        finally:
            master_db_connection.close()

    def teardown_environment(self, service_name="postgresql-x64-13"):
        """
        Tear down the database environment by unregistering the instance and stopping
        the PostgreSQL service if no other instances are running.
        """
        self.process_manager.unregister_instance()
        if not self.process_manager.any_other_instances_running():
            self.process_manager.stop_postgres_service(service_name)

    def is_initialized(self, db_name: str, db_user: str) -> bool:
        """
        Heuristic check to determine whether the database environment has already been
        prepared by `setup_environment`.

        Checks performed:
        - The target role/user exists in the cluster (pg_roles).
        - The `schema_migrations` table exists in the target database and the number
          of applied migrations is >= the number of migration files shipped with the
          project.

        This method is intentionally read-only and will not create databases, users,
        or run migrations.
        """
        # Basic validation
        try:
            if not is_valid_identifier(db_name) or not is_valid_identifier(db_user):
                self.logger.debug("is_initialized: invalid db_name or db_user identifier")
                return False
        except Exception:
            # If the identifier helper is not available for any reason, proceed with checks
            pass

        # 1) Verify user exists in the cluster using UserManager helper
        try:
            master_conn = self.get_master_db_connection()
            try:
                user_exists = self.user_manager.verify_user_exists(
                    master_db_connection=master_conn, username=db_user
                )
            finally:
                try:
                    master_conn.close()
                except Exception:
                    pass

            if not user_exists:
                self.logger.debug(f"is_initialized: user '{db_user}' not found")
                return False
        except Exception as e:
            self.logger.debug(f"is_initialized user check failed: {e}")
            return False

        # 2) Connect to the target database (read-only - do not create if missing)
        try:
            conn = self.database_manager.get_db_connection(
                db_name=db_name,
                username=self.master_db_user,
                password=self.master_db_password,
                create_if_not_exists=False,
            )
        except Exception as e:
            self.logger.debug(f"is_initialized: could not connect to target DB '{db_name}': {e}")
            return False

        try:
            is_migration_confirmed = self.migration_manager.verify_migrations(conn)
            if not is_migration_confirmed:
                self.logger.debug("is_initialized: migrations not confirmed")
                try:
                    conn.close()
                except Exception:
                    pass
                return False

            # 3) Verify privileges for the target user on the target database using UserManager helper
            master_conn_for_priv = None
            try:
                master_conn_for_priv = self.get_master_db_connection()
                has_privs = self.user_manager.verify_user_privileges(
                    master_db_connection=master_conn_for_priv,
                    target_db_connection=conn,
                    username=db_user,
                    db_name=db_name,
                )
            except Exception as e:
                self.logger.debug(f"is_initialized privilege verification failed: {e}")
                try:
                    conn.close()
                except Exception:
                    pass
                try:
                    if master_conn_for_priv:
                        master_conn_for_priv.close()
                except Exception:
                    pass
                return False
            finally:
                try:
                    if master_conn_for_priv:
                        master_conn_for_priv.close()
                except Exception:
                    pass

            if not has_privs:
                self.logger.debug(f"is_initialized: user '{db_user}' lacks required privileges on '{db_name}'")
                try:
                    conn.close()
                except Exception:
                    pass
                return False

            try:
                conn.close()
            except Exception:
                pass

            # All checks passed
            return True
        except Exception as e:
            self.logger.debug(f"is_initialized migration check failed: {e}")
            try:
                conn.close()
            except Exception:
                pass
            return False
