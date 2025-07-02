import numpy as np
import pandas as pd


def validate_portfolio_backtest_executor_output(output: dict) -> bool:
    """
    Validate the output structure of PortfolioBacktestExecutor.
    Returns True if valid, False otherwise.
    """
    required_keys = [
        "portfolio_values",
        "cash_history",
        "holdings_history",
        "final_cash",
        "final_holdings",
        "transactions",
        "metrics",
    ]
    if not isinstance(output, dict):
        return False
    for key in required_keys:
        if key not in output:
            return False
    if not isinstance(output["portfolio_values"], list):
        return False
    if not isinstance(output["cash_history"], list):
        return False
    if not isinstance(output["holdings_history"], list):
        return False
    if not (isinstance(output["final_cash"], (float, int))):
        return False
    if not (isinstance(output["final_holdings"], (list, np.ndarray))):
        return False
    if not isinstance(output["transactions"], list):
        return False
    if not isinstance(output["metrics"], dict):
        return False
    return True


def validate_portfolio_backtest_executor_input(data: pd.DataFrame) -> bool:
    """
    Validate the input matrix for PortfolioBacktestExecutor.
    Returns True if valid, False otherwise.
    """
    if not isinstance(data, pd.DataFrame):
        return False
    if data.empty:
        return False
    # All columns must be numeric
    if not all(pd.api.types.is_numeric_dtype(data[col]) for col in data.columns):
        return False
    # Index should be unique
    if not data.index.is_unique:
        return False
    # Optionally, check for datetime index (common in time series)
    # Uncomment if you want to enforce this:
    # if not pd.api.types.is_datetime64_any_dtype(data.index):
    #     return False
    return True
