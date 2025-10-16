from pathlib import Path
import psycopg2
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

    def verify_migrations(self, conn: psycopg2.extensions.connection) -> bool:
        """
        Confirm that all migration files have been applied to the database.
        Returns True if all migrations are applied, False otherwise.
        """
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass('public.schema_migrations');")
                res = cur.fetchone()
                if not res or res[0] is None:
                    self.logger.debug("is_initialized: schema_migrations table not found")
                    return False

                # Retrieve all applied migration versions (version column stores filenames/stems)
                cur.execute("SELECT version FROM schema_migrations;")
                rows = cur.fetchall()
                applied_versions = {r[0] for r in rows}
        except Exception as e:
            self.logger.debug(f"is_initialized migrations check failed: {e}")
            try:
                conn.close()
            except Exception:
                pass
            return False

        try:
            conn.close()
        except Exception:
            pass

        # Count migration files shipped with the project and compare explicit versions
        try:
            migrations_folder = Path(__file__).parent / "migrations"
            migration_files = sorted(migrations_folder.glob("*.sql"))
            migration_versions = [m.stem for m in migration_files]
        except Exception as e:
            self.logger.debug(f"is_initialized: failed to enumerate migration files: {e}")
            migration_versions = []

        missing = [v for v in migration_versions if v not in applied_versions]
        self.logger.debug(f"is_initialized: applied_versions={applied_versions} migration_files={migration_versions} missing={missing}")

        # Consider initialized only if there is at least one migration file and none are missing
        return len(migration_versions) > 0 and len(missing) == 0
