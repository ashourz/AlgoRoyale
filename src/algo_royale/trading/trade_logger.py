import alpaca_trade_api as tradeapi
import pandas as pd
from database.db import connect_db
import configparser


import sys
import os
import psycopg2
from database.db import connect_db  # Ensure correct import path

def log_trade(symbol, action, order_type, quantity, price=None, limit_price=None, status='PENDING'):
    """Insert a new trade into the trades table."""
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO trades (symbol, action, order_type, limit_price, quantity, price, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING trade_id, trade_time
        """, (symbol, action, order_type, limit_price, quantity, price, status))

        trade_id, trade_time = cur.fetchone()
        conn.commit()

        print(f"Trade logged: {action} {quantity} {symbol} at ${price or limit_price} ({order_type}, {status}) | Trade ID: {trade_id} | Time: {trade_time}")

    except Exception as e:
        print(f"Error logging trade: {e}")

    finally:
        cur.close()
        conn.close()

# Example Usage:
if __name__ == "__main__":
    log_trade("AAPL", "BUY", "LIMIT", 10, limit_price=150.5)
