# db/setup.py

from pathlib import Path
import psycopg2

def run_schema(conn):
    path = Path(__file__).parent / "schema.sql"
    with open(path, "r") as file:
        sql = file.read()

    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

# Usage Example:
if __name__ == "__main__":
    # Establish DB connection
    conn = psycopg2.connect("dbname=yourdb user=youruser password=yourpassword")
    
    # Run schema setup
    run_schema(conn)
    
    # Close the connection
    conn.close()