# setup_database.py

from db.migrations.migration_manager import apply_migrations
from config.db_config import get_db_connection, close_connection

def main():
    # Create a connection with `create_if_not_exists=True` to handle the database creation logic
    conn = get_db_connection(create_if_not_exists=True)
    
    # Apply migrations after ensuring the database is ready
    apply_migrations(conn)

    # Close the connection after migrations
    close_connection(conn)

if __name__ == "__main__":
    main()
