import psycopg2
import configparser
from config.config import DB_PARAMS  # Import DB credentials


def connect_db():
    """Connect to PostgreSQL and return a connection object."""
    return psycopg2.connect(**DB_PARAMS)

def create_tables():
    """Create a table for storing stock data."""
    conn = connect_db()
    cur = conn.cursor()

    # Stock Data Table  
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            timestamp TIMESTAMP,
            open FLOAT,
            high FLOAT,
            low FLOAT,
            close FLOAT,
            volume INT
        )
    """)

    # Trades Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            trade_id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            trade_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            action TEXT CHECK (action IN ('BUY', 'SELL')),
            order_type TEXT CHECK (order_type IN ('MARKET', 'LIMIT')),
            limit_price FLOAT NULL,
            quantity INT NOT NULL,
            price FLOAT NULL,
            status TEXT CHECK (status IN ('PENDING', 'FILLED', 'CANCELED')) DEFAULT 'PENDING'
        )
    """)

    # News Sentiment Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_sentiment (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            news_time TIMESTAMP,
            headline TEXT,
            sentiment_score FLOAT
        )
    """)

    # News Sentiment Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS news_sentiment (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            news_time TIMESTAMP,
            headline TEXT,
            sentiment_score FLOAT
        )
    """)


    conn.commit()

    ## Close Connection
    cur.close()
    conn.close()

# Run table creation on startup
if __name__ == "__main__":
    create_tables()
