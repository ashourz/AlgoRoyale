from contextlib import contextmanager
from typing import Generator

import psycopg2

from algo_royale.clients.db.database_admin import DatabaseAdmin
from algo_royale.logging.loggable import Loggable


class Database:
    def __init__(
        self,
        database_admin: DatabaseAdmin,
        db_name: str,
        db_user: str,
        db_password: str,
        logger: Loggable,
    ):
        self.database_admin = database_admin
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.logger = logger
        self.connection = None

    def connect(self) -> psycopg2.extensions.connection:
        """
        Connect to the database.
        """
        self.connection = self.database_admin.get_db_connection(
            db_name=self.db_name,
            username=self.db_user,
            password=self.db_password,
        )
        return self.connection

    def disconnect(self):
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
            self.disconnect()

    def execute_query(self, query: str, params=None):
        """
        Execute a SQL query.
        """
        with self.connection_context() as conn:
            with conn.cursor() as cur:
                self.logger.debug(f"Executing query: {query} with params: {params}")
                cur.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    results = cur.fetchall()
                    self.logger.debug(f"Query results: {results}")
                    return results
                else:
                    conn.commit()
                    self.logger.info("✅ Query executed and changes committed.")

    def drop_all_tables(self):
        """
        Drop all tables in the database. Use with caution!
        """
        drop_tables_query = """
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
        """
        self.execute_query(drop_tables_query)
        self.logger.info("✅ All tables dropped from the database.")
