import os
import pandas as pd
from datetime import datetime

from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
logger = LoggerSingleton(LoggerType.BACKTESTING, Environment.PRODUCTION).get_logger()

def save_results(strategy_name: str, symbol: str, results_df: pd.DataFrame):
    """
    Save backtest results to a CSV file.
    
    Args:
        strategy_name (str): Name of the strategy used.
        symbol (str): Ticker symbol for the asset.
        results_df (pd.DataFrame): DataFrame containing backtest results.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{strategy_name}_{symbol}_{timestamp}.csv"
    filepath = os.path.join(RESULTS_DIR, filename)

    results_df.to_csv(filepath, index=False)
    logger.info(f"[+] Results saved to: {filepath}")
