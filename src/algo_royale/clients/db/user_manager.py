import re

import psycopg2


class UserManager:
    def __init__(
        self,
        logger,
    ):
        self.logger = logger

    def is_valid_identifier(identifier):
        return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier) is not None

    def is_valid_password(password):
        return isinstance(password, str) and len(password) >= 8

    def create_user(
        self,
        master_db_connection: psycopg2.extensions.connection,
        username: str,
        password: str,
    ):
        if not self.is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")
        if not self.is_valid_password(password):
            raise ValueError("Password must be at least 8 characters long.")
        try:
            self.logger.info(f"🛠️ Ensuring user '{username}' exists...")
            with master_db_connection.cursor() as cur:
                cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{username}'")
                if not cur.fetchone():
                    self.logger.info(f"🛠️ Creating user: {username}")
                    cur.execute(f"CREATE USER {username} WITH PASSWORD %s", (password,))
                    self.logger.info(f"✅ Created user: {username}")
                else:
                    self.logger.info(
                        f"ℹ️ User already exists: {username}. Updating password."
                    )
                    cur.execute(f"ALTER USER {username} WITH PASSWORD %s", (password,))
                    self.logger.info(f"🔑 Updated password for user: {username}")
        except Exception as e:
            self.logger.error(f"❌ Error creating/updating user '{username}': {e}")
            raise

    def delete_user(
        self,
        master_db_connection: psycopg2.extensions.connection,
        username: str,
    ):
        if not self.is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")
        self.logger.info(f"🛠️ Deleting user '{username}' if exists...")
        try:
            # Connect to the default 'postgres' database to perform user deletion
            with master_db_connection.cursor() as cur:
                cur.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{username}'")
                if cur.fetchone():
                    self.logger.info(f"🛠️ Deleting user: {username}")
                    cur.execute(f"DROP USER {username}")
                    self.logger.info(f"✅ Deleted user: {username}")
                else:
                    self.logger.info(
                        f"ℹ️ User does not exist: {username}. No action taken."
                    )
        except Exception as e:
            self.logger.error(f"❌ Error deleting user '{username}': {e}")
            raise

    def grant_privileges(
        self,
        master_db_connection: psycopg2.extensions.connection,
        target_db_connection: psycopg2.extensions.connection,
        db_name: str,
        username: str,
    ):
        if not self.is_valid_identifier(db_name):
            raise ValueError(f"Invalid database name: {db_name}")
        if not self.is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")
        try:
            self.logger.info(
                f"🛠️ Granting privileges on '{db_name}' to user '{username}'..."
            )
            # Grant connect privilege on the database using master connection
            with master_db_connection.cursor() as cur:
                cur.execute(f"GRANT CONNECT ON DATABASE {db_name} TO {username}")
                self.logger.info(f"✅ Granted CONNECT on {db_name} to {username}")
            # Now connect to the target database to grant schema/table privileges

            with target_db_connection.cursor() as cur:
                cur.execute(f"GRANT USAGE ON SCHEMA public TO {username}")
                self.logger.info(f"✅ Granted USAGE on schema public to {username}")
                cur.execute(
                    f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {username}"
                )
                self.logger.info(
                    f"✅ Granted ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to {username}"
                )
                cur.execute(
                    f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {username}"
                )
                self.logger.info(
                    f"✅ Set default privileges for future tables in schema public for {username}"
                )
        except Exception as e:
            self.logger.error(
                f"❌ Error granting privileges on '{db_name}' to user '{username}': {e}"
            )
            raise
