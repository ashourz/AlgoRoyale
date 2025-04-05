import alpaca_trade_api as tradeapi
import pandas as pd
from db import connect_db
import configparser

# Load config
config = configparser.ConfigParser()
config.read("config.ini")

# Alpaca API credentials
ALPACA_API_KEY = config["alpaca"]["api_key"]
ALPACA_API_SECRET = config["alpaca"]["api_secret"]
BASE_URL = config["alpaca"]["base_url"]

# Initialize Alpaca API
api = tradeapi.REST(ALPACA_API_KEY, ALPACA_API_SECRET, BASE_URL, api_version='v2')

def fetch_historical_data(symbol, start_date, end_date, timeframe="1Min"):
    """Fetch historical stock data from Alpaca and store in PostgreSQL."""
    bars = api.get_barset(symbol, timeframe, limit=1000).df
    bars = bars[symbol]
    
    conn = connect_db()
    cur = conn.cursor()
    
    for index, row in bars.iterrows():
        cur.execute(
            """
            INSERT INTO stock_data (symbol, timestamp, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (symbol, index, row['open'], row['high'], row['low'], row['close'], row['volume']),
        )

    conn.commit()
    cur.close()
    conn.close()
    
    return bars

# Example usage:
if __name__ == "__main__":
    print(fetch_historical_data("AAPL", "2024-01-01", "2024-06-01"))


## Retrieves all trade data from trades.
def get_trade_history():
    """Fetch all trades from the database."""
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM trades ORDER BY trade_time DESC", conn)
    conn.close()
    return df

# Example Usage
print(get_trade_history())


## Stores news headlines and their sentiment score.
def store_news_sentiment(symbol, headline, sentiment_score):
    """Store news sentiment data in the database."""
    conn = connect_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO news_sentiment (symbol, news_time, headline, sentiment_score)
        VALUES (%s, NOW(), %s, %s)
    """, (symbol, headline, sentiment_score))

    conn.commit()
    cur.close()
    conn.close()
    print(f"News stored for {symbol}: {headline} (Score: {sentiment_score})")

# Example Usage
store_news_sentiment("AAPL", "Apple announces new AI chip", 0.85)


