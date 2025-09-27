import psycopg2


class UserManager:
    def __init__(
        self,
        logger,
    ):
        self.logger = logger

    def create_user(
        self,
        master_db_connection: psycopg2.extensions.connection,
        username: str,
        password: str,
    ):
        self.logger.info(f"🛠️ Ensuring user '{username}' exists...")

        with master_db_connection.cursor() as cur:
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

    def grant_privileges(
        self,
        master_db_connection: psycopg2.extensions.connection,
        target_db_connection: psycopg2.extensions.connection,
        db_name: str,
        username: str,
    ):
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
