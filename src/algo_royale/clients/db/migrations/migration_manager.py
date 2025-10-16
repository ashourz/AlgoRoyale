from pathlib import Path
import psycopg2
from psycopg2 import sql
from algo_royale.logging.loggable import Loggable


class MigrationManager:
    """
    Manages database schema migrations safely.
    Each migration runs in its own transaction.
    Supports multi-instance deployments using advisory locks.
    """

    def __init__(self, logger: Loggable):
        self.logger = logger

    def apply_migrations(self, conn: psycopg2.extensions.connection):
        """
        Apply pending migrations from the migrations folder to the database.
        """
        migrations_folder = Path(__file__).parent / "migrations"
        self.logger.info(f"Looking for migration files in {migrations_folder}")

        migrations_files = sorted(migrations_folder.glob("*.sql"))
        self.logger.info(f"Found {len(migrations_files)} migration files.")

        with conn.cursor() as cur:
            # Ensure migrations table exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            self.logger.info("schema_migrations table is ready.")

        # Acquire an advisory lock to prevent race conditions if multiple instances run migrations
        lock_id = 123456789  # arbitrary unique integer
        with conn.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_lock(%s);", (lock_id,))
            locked = cur.fetchone()[0]
            if not locked:
                self.logger.warning("Another instance is running migrations. Skipping.")
                return

        try:
            for migration in migrations_files:
                version = migration.stem

                with conn.cursor() as cur:
                    cur.execute("SELECT 1 FROM schema_migrations WHERE version = %s;", (version,))
                    if cur.fetchone():
                        self.logger.info(f"Migration {version} already applied. Skipping.")
                        continue

                # Apply migration inside a transaction
                try:
                    with conn:
                        with conn.cursor() as cur:
                            self.logger.info(f"Applying migration {version}...")
                            schema_sql = migration.read_text()
                            cur.execute(schema_sql)
                            cur.execute(
                                "INSERT INTO schema_migrations (version) VALUES (%s);",
                                (version,)
                            )
                            self.logger.info(f"✅ Successfully applied migration {version}")
                except Exception as e:
                    self.logger.error(f"Failed to apply migration {version}: {e}")
                    raise

        finally:
            # Release advisory lock
            with conn.cursor() as cur:
                cur.execute("SELECT pg_advisory_unlock(%s);", (lock_id,))
            self.logger.info("Migration process completed.")
