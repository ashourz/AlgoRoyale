import os
import pandas as pd
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

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
    print(f"[+] Results saved to: {filepath}")
