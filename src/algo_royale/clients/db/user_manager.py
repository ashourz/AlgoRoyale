import psycopg2
from psycopg2 import sql

from algo_royale.clients.db.db_utils import is_valid_identifier


class UserManager:
    def __init__(self, logger):
        self.logger = logger

    def is_valid_password(self, password):
        return isinstance(password, str) and len(password) >= 8

    def create_user(
        self,
        master_db_connection: psycopg2.extensions.connection,
        username: str,
        password: str,
    ):
        if not is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")
        if not self.is_valid_password(password):
            raise ValueError("Password must be at least 8 characters long.")
        try:
            self.logger.info(f"🛠️ Ensuring user '{username}' exists...")
            with master_db_connection.cursor() as cur:
                # Use parameterized query for value checks
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
                if not cur.fetchone():
                    self.logger.info(f"🛠️ Creating user: {username}")
                    # Use Identifier for the username identifier and parameterize the password
                    cur.execute(
                        sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                            sql.Identifier(username)
                        ),
                        (password,),
                    )
                    self.logger.info(f"✅ Created user: {username}")
                else:
                    self.logger.info(
                        f"ℹ️ User already exists: {username}. Updating password."
                    )
                    cur.execute(
                        sql.SQL("ALTER USER {} WITH PASSWORD %s").format(
                            sql.Identifier(username)
                        ),
                        (password,),
                    )
                    self.logger.info(f"🔑 Updated password for user: {username}")
        except Exception as e:
            self.logger.error(f"❌ Error creating/updating user '{username}': {e}")
            raise

    def delete_user(
        self,
        master_db_connection: psycopg2.extensions.connection,
        username: str,
    ):
        if not is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")
        self.logger.info(f"🛠️ Deleting user '{username}' if exists...")
        try:
            # DROP USER must run with autocommit when terminating connections; ensure isolation set by caller if needed
            with master_db_connection.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
                if cur.fetchone():
                    self.logger.info(f"🛠️ Deleting user: {username}")
                    cur.execute(
                        sql.SQL("DROP USER {};").format(sql.Identifier(username))
                    )
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
        if not is_valid_identifier(db_name):
            raise ValueError(f"Invalid database name: {db_name}")
        if not is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")
        try:
            self.logger.info(
                f"🛠️ Granting privileges on '{db_name}' to user '{username}'..."
            )
            # Grant connect privilege on the database using master connection
            with master_db_connection.cursor() as cur:
                cur.execute(
                    sql.SQL("GRANT CONNECT ON DATABASE {} TO {};").format(
                        sql.Identifier(db_name), sql.Identifier(username)
                    )
                )
                self.logger.info(f"✅ Granted CONNECT on {db_name} to {username}")
            # Now connect to the target database to grant schema/table privileges

            with target_db_connection.cursor() as cur:
                cur.execute(
                    sql.SQL("GRANT USAGE ON SCHEMA public TO {};").format(
                        sql.Identifier(username)
                    )
                )
                self.logger.info(f"✅ Granted USAGE on schema public to {username}")
                cur.execute(
                    sql.SQL(
                        "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {};"
                    ).format(sql.Identifier(username))
                )
                self.logger.info(
                    f"✅ Granted ALL PRIVILEGES ON ALL TABLES IN SCHEMA public to {username}"
                )
                cur.execute(
                    sql.SQL(
                        "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {};"
                    ).format(sql.Identifier(username))
                )
                self.logger.info(
                    f"✅ Set default privileges for future tables in schema public for {username}"
                )
        except Exception as e:
            self.logger.error(
                f"❌ Error granting privileges on '{db_name}' to user '{username}': {e}"
            )
            raise

    def verify_user_exists(
        self,
        master_db_connection: psycopg2.extensions.connection,
        username: str,
    ) -> bool:
        if not is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")
        try:
            with master_db_connection.cursor() as cur:
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
                exists = cur.fetchone() is not None
                self.logger.debug(
                    f"User '{username}' existence check: {'found' if exists else 'not found'}"
                )
                return exists
        except Exception as e:
            self.logger.error(
                f"❌ Error verifying existence of user '{username}': {e}"
            )
            raise
        
    def verify_user_privileges(
        self,
        master_db_connection: psycopg2.extensions.connection,
        target_db_connection: psycopg2.extensions.connection,
        username: str,
        db_name: str = None,
    ) -> bool:
        """
        Verify that the specified user has the privileges granted by `grant_privileges`:
        - CONNECT on the database
        - USAGE on schema public
        - ALL privileges on all tables in schema public (i.e. a grant exists per table)
        - Default ACL entries granting the user (best-effort check)

        master_db_connection is required. db_name is optional; if omitted we attempt
        to infer it from the target_db_connection.
        """
        if not is_valid_identifier(username):
            raise ValueError(f"Invalid username: {username}")

        if master_db_connection is None:
            raise ValueError("master_db_connection is required for privilege verification")

        try:
            # Determine current database name if not explicitly provided
            if not db_name:
                try:
                    with target_db_connection.cursor() as cur:
                        cur.execute("SELECT current_database();")
                        db_name = cur.fetchone()[0]
                except Exception:
                    db_name = None

            # 1) Check CONNECT privilege on database (use master connection)
            try:
                with master_db_connection.cursor() as cur:
                    # has_database_privilege(user, db, priv) -> boolean
                    cur.execute(
                        "SELECT has_database_privilege(%s, %s, 'CONNECT');",
                        (username, db_name),
                    )
                    has_connect = bool(cur.fetchone()[0])
                if not has_connect:
                    self.logger.debug(f"verify_user_privileges: user '{username}' lacks CONNECT on '{db_name}'")
                    return False
            except Exception as e:
                self.logger.debug(f"verify_user_privileges: database CONNECT check failed: {e}")
                return False

            # 2) Check USAGE on schema public and table-level grants
            try:
                with target_db_connection.cursor() as cur:
                    cur.execute(
                        "SELECT has_schema_privilege(%s, 'public', 'USAGE');",
                        (username,),
                    )
                    has_usage = bool(cur.fetchone()[0])
                    if not has_usage:
                        self.logger.debug(f"verify_user_privileges: user '{username}' lacks USAGE on schema public")
                        return False

                    # Ensure ALL existing tables in public schema have grants for the user
                    cur.execute(
                        ""
                        "SELECT COUNT(1) FROM information_schema.tables t\n"
                        "WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'"
                        " AND NOT EXISTS (SELECT 1 FROM information_schema.role_table_grants g "
                        "WHERE g.grantee = %s AND g.table_schema = 'public' AND g.table_name = t.table_name);",
                        (username,),
                    )
                    missing_grants = cur.fetchone()[0]
                    if missing_grants > 0:
                        self.logger.debug(f"verify_user_privileges: user '{username}' missing grants on {missing_grants} public tables")
                        return False

                    # Best-effort: check for default ACL entries granting the user
                    # pg_default_acl.defaclacl contains ACL items; we'll do a text-search for username
                    cur.execute(
                        "SELECT 1 FROM pg_default_acl WHERE defaclacl::text LIKE %s LIMIT 1;",
                        (f"%{username}=%",),
                    )
                    has_default_acl = cur.fetchone() is not None
                    if not has_default_acl:
                        # Not necessarily fatal, but warn and treat as failure for strict checking
                        self.logger.debug(f"verify_user_privileges: no default ACL entries found for '{username}'")
                        return False

                # All checks passed
                self.logger.debug(f"verify_user_privileges: user '{username}' has expected privileges on DB '{db_name}'")
                return True
            except Exception as e:
                self.logger.debug(f"verify_user_privileges: schema/table privilege checks failed: {e}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error verifying privileges of user '{username}': {e}")
            raise