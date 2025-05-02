
from algo_royale.trade_another_day.utils.data_loader import BacktestDataLoader

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

class BacktestEngine:
    def __init__(self, fetch_if_missing=True):
        self.fetch_if_missing = fetch_if_missing
        self.logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()
        self.loader = BacktestDataLoader()
        self.data = None

    def load_data(self):
        """
        Load data for all symbols in the watchlist.
        """
        self.logger.info("Loading data for all symbols in the watchlist...")
        self.data = self.loader.load_all(self.fetch_if_missing)
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
