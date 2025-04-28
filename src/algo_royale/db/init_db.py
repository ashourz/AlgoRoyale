from algo_royale.db.migrations.migration_manager import apply_migrations
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config.config import DB_PARAMS, DB_SECRETS  # Import DB credentials

def create_database_if_not_exists(dbname, user, password, host="localhost"):
    """
    Check if the database exists. If not, create it.
    """
    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Allows CREATE DATABASE

    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{dbname}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {dbname}")
            print(f"✅ Created database: {dbname}")
        else:
            print(f"ℹ️ Database already exists: {dbname}")

    conn.close()


def main():
    # Use the imported DB_PARAMS directly for connection
    dbname = DB_PARAMS["dbname"]
    user = DB_PARAMS["user"]
    password = DB_SECRETS["password"]
    host = DB_PARAMS["host"]
    port = DB_PARAMS["port"]

    # Step 1: Create the database if it doesn't exist
    create_database_if_not_exists(dbname, user, password, host)

    # Step 2: Connect to the created or existing database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)

    # Step 3: Apply migrations using the migration manager (delegated)
    apply_migrations(conn)

    # Close the connection
    conn.close()


if __name__ == "__main__":
    main()
