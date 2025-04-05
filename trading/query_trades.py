import psycopg2
from database.db import connect_db  # Ensure correct import path

def get_trades(symbol=None):
    """Fetch all trades or filter by symbol, and print them in rows."""
    try:
        conn = connect_db()
        cur = conn.cursor()

        if symbol:
            cur.execute("SELECT * FROM trades WHERE symbol = %s ORDER BY trade_time DESC", (symbol,))
        else:
            cur.execute("SELECT * FROM trades ORDER BY trade_time DESC")

        trades = cur.fetchall()
        conn.close()

        if not trades:
            print("No trades found.")
            return
        
        # Print table header
        print("\n{:<5} {:<6} {:<20} {:<6} {:<10} {:<12} {:<8} {:<10} {:<10}".format(
            "ID", "Symbol", "Trade Time", "Action", "Order Type", "Limit Price", "Qty", "Price", "Status"
        ))
        print("-" * 95)

        # Print each trade in a row
        for trade in trades:
            print("{:<5} {:<6} {:<20} {:<6} {:<10} {:<12} {:<8} {:<10} {:<10}".format(*trade))

    except Exception as e:
        print(f"Error fetching trades: {e}")

# Example Usage:
if __name__ == "__main__":
    print("\nAll Trades:")
    get_trades()

    print("\nAAPL Trades:")
    get_trades("AAPL")
