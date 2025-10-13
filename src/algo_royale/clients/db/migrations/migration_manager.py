from pathlib import Path

import psycopg2

from algo_royale.logging.loggable import Loggable


class MigrationManager:
    """
    Manages database schema migrations.
    """

    def __init__(self, logger: Loggable):
        self.logger = logger

    def apply_migrations(self, conn: psycopg2.extensions.connection):
        """
        Apply the pending migrations to the database.
        """
        # Get the list of all migration files from the migrations directory
        migrations_folder = Path(__file__).parent
        self.logger.info(f"Looking for migration files in {migrations_folder}")
        migrations_files = sorted(
            migrations_folder.glob("*.sql")
        )  # Sort to apply in order
        self.logger.info(f"Found {len(migrations_files)} migration files.")

        with conn.cursor() as cur:
            # Ensure the migrations table exists
            self.logger.info("Ensuring schema_migrations table exists...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(50) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.logger.info("schema_migrations table is ready.")
            conn.commit()
            # Get the list of applied migrations
            cur.execute("SELECT version FROM schema_migrations;")
            applied_versions = {row[0] for row in cur.fetchall()}
            self.logger.info(f"Already applied migrations: {applied_versions}")
            # Apply each migration that hasn't been applied yet
            for migration in migrations_files:
                version = (
                    migration.stem
                )  # Use the file name without extension as version

                if version not in applied_versions:
                    with open(migration, "r") as file:
                        schema_sql = file.read()
                        cur.execute(schema_sql)
                        self.logger.info(
                            f"✅ Applied migration {version} by {migration.name}"
                        )

                    # Log the applied migration in the schema_migrations table
                    cur.execute(
                        """
                        INSERT INTO schema_migrations (version) 
                        VALUES (%s);
                    """,
                        (version,),
                    )
                    conn.commit()
