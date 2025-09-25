import time
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from algo_royale.logging.loggable import Loggable


class Database:
    @classmethod
    def initialize_app_db(
        cls,
        master_db_name,
        master_db_user,
        master_db_password,
        db_name,
        db_user,
        db_password,
        db_host,
        db_port,
        logger,
        service_name="postgresql-x64-13",
    ):
        """
        Register PID, start the DB service if needed, and return a Database instance.
        """
        cls.register_instance()
        if not cls.is_postgres_running(db_host, db_port):
            started = cls.start_postgres_service(service_name)
            if not started:
                raise RuntimeError(
                    f"Could not start PostgreSQL service '{service_name}' on {db_host}:{db_port}"
                )
        # Optionally: register user logic here
        return cls(
            master_db_name=master_db_name,
            master_db_user=master_db_user,
            master_db_password=master_db_password,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            db_host=db_host,
            db_port=db_port,
            logger=logger,
        )

    def close(self):
        """Close DB connection, unregister PID, and stop service if no other app instances remain."""
        # ...existing close logic if any...
        Database.unregister_instance()
        if not Database.any_other_instances_running():
            Database.stop_postgres_service()

    _PID_FILE = "algo_royale_app.pids"

    def __init__(
        self,
        master_db_name: str,
        master_db_user: str,
        master_db_password: str,
        db_name: str,
        db_user: str,
        db_password: str,
        db_host: str,
        db_port: int,
        logger: Loggable,
    ):
        self.logger = logger
        self.master_db_name = master_db_name
        self.master_db_user = master_db_user
        self.master_db_password = master_db_password
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.connection = None

    def connect(
        self, retries=3, delay=2, create_if_not_exists=False
    ) -> psycopg2.extensions.connection:
        """
        Establish a connection to the database. Optionally create the database if it doesn't exist.
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
                self.logger.info("✅ Connected to the master database.")
                if create_if_not_exists:
                    self.logger.info(f"🛠️ Ensuring database '{self.db_name}' exists...")
                    # Check if the target database exists; create it if it doesn't
                    with conn.cursor() as cur:
                        cur.execute(
                            f"SELECT 1 FROM pg_database WHERE datname = '{self.db_name}'"
                        )
                        if not cur.fetchone():
                            self.logger.info(f"🛠️ Creating database: {self.db_name}")
                            cur.execute(f"CREATE DATABASE {self.db_name}")
                            self.logger.info(f"✅ Created database: {self.db_name}")
                        else:
                            self.logger.info(
                                f"ℹ️ Database already exists: {self.db_name}"
                            )

                # Connect to the target database
                self.logger.info("🔗 Connecting to the target database...")
                self.connection = psycopg2.connect(
                    dbname=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
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

    def close(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()
            self.logger.info("✅ Database connection closed.")

    @contextmanager
    def connection_context(
        self, create_if_not_exists=False
    ) -> Generator[psycopg2.extensions.connection, None, None]:
        """
        Context manager for database connections.
        """
        try:
            self.logger.info("🔗 Connecting to the database...")
            conn = self.connect(create_if_not_exists=create_if_not_exists)
            yield conn
        except Exception as e:
            self.logger.error(f"❌ Error during database operation: {e}")
            raise
        finally:
            self.close()

    def create_user(self, username, password):
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        self.logger.info(f"🛠️ Ensuring user '{username}' exists...")
        conn = psycopg2.connect(
            dbname=self.master_db_name,
            user=self.master_db_user,
            password=self.master_db_password,
            host=self.db_host,
            port=self.db_port,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{username}'")
            if not cur.fetchone():
                self.logger.info(f"🛠️ Creating user: {username}")
                cur.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
                self.logger.info(f"✅ Created user: {username}")
            else:
                self.logger.info(
                    f"ℹ️ User already exists: {username}. Updating password."
                )
                cur.execute(f"ALTER USER {username} WITH PASSWORD '{password}'")
                self.logger.info(f"🔑 Updated password for user: {username}")
        conn.close()

    def grant_privileges(self, dbname, username):
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        self.logger.info(f"🛠️ Granting privileges on '{dbname}' to user '{username}'...")
        conn = psycopg2.connect(
            dbname=self.master_db_name,
            user=self.master_db_user,
            password=self.master_db_password,
            host=self.db_host,
            port=self.db_port,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {username}")
            self.logger.info(f"✅ Granted privileges on {dbname} to {username}")
        conn.close()

    @staticmethod
    def stop_postgres_service(service_name: str = "postgresql-x64-13") -> bool:
        """Attempt to stop the PostgreSQL service on Windows. Returns True if stopped or already stopped."""
        import platform
        import subprocess

        if platform.system() != "Windows":
            raise NotImplementedError(
                "stop_postgres_service is only implemented for Windows."
            )
        try:
            # First, check if the service is already stopped
            query = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            if "STOPPED" in query.stdout:
                return True
            # Try to stop the service
            result = subprocess.run(
                ["sc", "stop", service_name], capture_output=True, text=True
            )
            if (
                "STOP_PENDING" in result.stdout
                or "STOPPED" in result.stdout
                or result.returncode == 0
            ):
                return True
            # If already stopped, that's fine
            if "already stopped" in result.stdout.lower():
                return True
            return False
        except Exception as e:
            print(f"Error stopping PostgreSQL service: {e}")
            return False

    @staticmethod
    def is_postgres_running(host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a PostgreSQL server is accepting connections on the given host/port."""
        import socket

        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except (OSError, ConnectionRefusedError):
            return False

    @staticmethod
    def start_postgres_service(service_name: str = "postgresql-x64-13") -> bool:
        """Attempt to start the PostgreSQL service on Windows. Returns True if started or already running."""
        import platform
        import subprocess

        if platform.system() != "Windows":
            raise NotImplementedError(
                "start_postgres_service is only implemented for Windows."
            )
        try:
            # First, check if the service is already running
            query = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            if "RUNNING" in query.stdout:
                return True
            # Try to start the service
            result = subprocess.run(
                ["sc", "start", service_name], capture_output=True, text=True
            )
            if (
                "START_PENDING" in result.stdout
                or "RUNNING" in result.stdout
                or result.returncode == 0
            ):
                return True
            # If already running, that's fine
            if "already running" in result.stdout.lower():
                return True
            return False
        except Exception as e:
            print(f"Error starting PostgreSQL service: {e}")
            return False

    @staticmethod
    def register_instance():
        """Register this process's PID in the shared PID file."""
        import os

        pid = os.getpid()
        try:
            with open(Database._PID_FILE, "a") as f:
                f.write(f"{pid}\n")
        except Exception as e:
            print(f"Error registering PID: {e}")

    @staticmethod
    def unregister_instance():
        """Remove this process's PID from the shared PID file."""
        import os

        pid = os.getpid()
        try:
            if not os.path.exists(Database._PID_FILE):
                return
            with open(Database._PID_FILE, "r") as f:
                pids = [line.strip() for line in f if line.strip()]
            pids = [p for p in pids if p != str(pid)]
            with open(Database._PID_FILE, "w") as f:
                for p in pids:
                    f.write(f"{p}\n")
        except Exception as e:
            print(f"Error unregistering PID: {e}")

    @staticmethod
    def any_other_instances_running() -> bool:
        """Check if any other registered PIDs are still running."""
        import os

        import psutil

        pid = os.getpid()
        if not os.path.exists(Database._PID_FILE):
            return False
        try:
            with open(Database._PID_FILE, "r") as f:
                pids = [
                    int(line.strip())
                    for line in f
                    if line.strip() and line.strip().isdigit()
                ]
            for p in pids:
                if p != pid and psutil.pid_exists(p):
                    return True
            return False
        except Exception as e:
            print(f"Error checking other instances: {e}")
            return False
