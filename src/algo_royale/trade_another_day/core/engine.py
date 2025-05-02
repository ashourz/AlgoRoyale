
from algo_royale.trade_another_day.utils.data_loader import load_all_symbol_data_from_watchlist

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

class BacktestEngine:
    def __init__(self, config, fetch_if_missing=True):
        self.watchlist_path = config['watchlist_path']
        self.data_dir = config['data_dir']
        self.fetch_if_missing = fetch_if_missing
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION)
        self.data = None

    def load_data(self):
        """
        Load data for all symbols in the watchlist.
        """
        self.logger.info("Loading data for all symbols in the watchlist...")
        self.data = load_all_symbol_data_from_watchlist(self.watchlist_path, self.data_dir, self.fetch_if_missing)
        self.logger.info(f"Loaded data for {len(self.data)} symbols.")

    def run_backtest(self):
        """
        Run the backtest using the loaded data.
        """
        if self.data is None:
            raise ValueError("Data has not been loaded. Please load data before running the backtest.")

        self.logger.info("Running backtest...")
        # Example of iterating through symbols and their data for backtest logic
        for symbol, df in self.data.items():
            # Implement your backtest logic here
            self.logger.info(f"Running backtest for {symbol}...")

        self.logger.info("Backtest complete.")
