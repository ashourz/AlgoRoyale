import os

from trade_another_day.utils.data_loader import load_all_symbol_data_from_watchlist

class BacktestEngine:
    def __init__(self, config, fetch_if_missing=True):
        self.watchlist_path = config['watchlist_path']
        self.data_dir = config['data_dir']
        self.fetch_if_missing = fetch_if_missing
        self.data = None

    def load_data(self):
        """
        Load data for all symbols in the watchlist.
        """
        print("[INFO] Loading data for all symbols in the watchlist...")
        self.data = load_all_symbol_data_from_watchlist(self.watchlist_path, self.data_dir, self.fetch_if_missing)
        print(f"[INFO] Loaded data for {len(self.data)} symbols.")

    def run_backtest(self):
        """
        Run the backtest using the loaded data.
        """
        if self.data is None:
            raise ValueError("Data has not been loaded. Please load data before running the backtest.")

        print("[INFO] Running backtest...")
        # Example of iterating through symbols and their data for backtest logic
        for symbol, df in self.data.items():
            # Implement your backtest logic here
            print(f"[INFO] Running backtest for {symbol}...")

        print("[INFO] Backtest complete.")
