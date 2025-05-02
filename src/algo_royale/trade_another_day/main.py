
from algo_royale.trade_another_day.core.engine import BacktestEngine

from algo_royale.trade_another_day.config.config import load_config

def run_backtest():
    # Load the configuration settings
    config = load_config()
    watchlist_path = config['watchlist_path']
    data_dir = config['data_dir']

    # Initialize the BacktestEngine
    backtest_engine = BacktestEngine(fetch_if_missing=True)

    # Load the data for the backtest
    backtest_engine.load_data()

    # Run the backtest
    backtest_engine.run_backtest()

if __name__ == "__main__":
    run_backtest()