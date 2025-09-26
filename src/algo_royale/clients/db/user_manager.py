import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class UserManager:
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
        self.db_host = db_host
        self.db_port = db_port
        self.logger = logger

    def create_user(self, username, password):
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

    def grant_privileges(self, db_name, username):
        self.logger.info(
            f"🛠️ Granting privileges on '{db_name}' to user '{username}'..."
        )
        conn = psycopg2.connect(
            dbname=self.master_db_name,
            user=self.master_db_user,
            password=self.master_db_password,
            host=self.db_host,
            port=self.db_port,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username}")
            self.logger.info(f"✅ Granted privileges on {db_name} to {username}")
        conn.close()
