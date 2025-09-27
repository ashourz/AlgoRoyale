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
        db_name: str,
        username: str,
    ):
        self.logger.info(
            f"🛠️ Granting privileges on '{db_name}' to user '{username}'..."
        )
        with master_db_connection.cursor() as cur:
            cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username}")
            self.logger.info(f"✅ Granted privileges on {db_name} to {username}")
