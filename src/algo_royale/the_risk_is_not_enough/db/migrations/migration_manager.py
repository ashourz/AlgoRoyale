from pathlib import Path

from logger.logger_singleton import Environment, LoggerSingleton, LoggerType

logger = LoggerSingleton(LoggerType.TRADING, Environment.PRODUCTION)

def apply_migrations(conn):
    """
    Apply the pending migrations to the database.
    """
    # Get the list of all migration files from the migrations directory
    migrations_folder = Path(__file__).parent / "migrations"
    migrations_files = sorted(migrations_folder.glob("*.sql"))  # Sort to apply in order
    
    with conn.cursor() as cur:
        # Ensure the migrations table exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Get the list of applied migrations
        cur.execute("SELECT version FROM schema_migrations;")
        applied_versions = {row[0] for row in cur.fetchall()}
        
        # Apply each migration that hasn't been applied yet
        for migration in migrations_files:
            version = migration.stem  # Use the file name without extension as version
            
            if version not in applied_versions:
                with open(migration, "r") as file:
                    schema_sql = file.read()
                    cur.execute(schema_sql)
                    logger.info(f"✅ Applied migration {version}")
                
                # Log the applied migration in the schema_migrations table
                cur.execute("""
                    INSERT INTO schema_migrations (version) 
                    VALUES (%s);
                """, (version,))
                conn.commit()