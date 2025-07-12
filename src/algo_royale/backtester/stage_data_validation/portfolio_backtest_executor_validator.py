import numpy as np
import pandas as pd
from algo_royale.logging.loggable import Loggable


def validate_portfolio_backtest_executor_output(output: dict, logger: Loggable) -> bool:
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
        logger.warning(f"Validation failed: Not a dict. Value: {output}")
        return False
    for key in required_keys:
        if key not in output:
            logger.warning(f"Validation failed: '{key}' missing. Value: {output}")
            return False
    if not isinstance(output["portfolio_values"], list):
        logger.warning(
            f"Validation failed: 'portfolio_values' not list. Value: {output['portfolio_values']}"
        )
        return False
    if not isinstance(output["cash_history"], list):
        logger.warning(
            f"Validation failed: 'cash_history' not list. Value: {output['cash_history']}"
        )
        return False
    if not isinstance(output["holdings_history"], list):
        logger.warning(
            f"Validation failed: 'holdings_history' not list. Value: {output['holdings_history']}"
        )
        return False
    if not (isinstance(output["final_cash"], (float, int))):
        logger.warning(
            f"Validation failed: 'final_cash' not float or int. Value: {output['final_cash']}"
        )
        return False
    if not (isinstance(output["final_holdings"], (list, np.ndarray))):
        logger.warning(
            f"Validation failed: 'final_holdings' not list or ndarray. Value: {output['final_holdings']}"
        )
        return False
    if not isinstance(output["transactions"], list):
        logger.warning(
            f"Validation failed: 'transactions' not list. Value: {output['transactions']}"
        )
        return False
    if not isinstance(output["metrics"], dict):
        logger.warning(
            f"Validation failed: 'metrics' not dict. Value: {output['metrics']}"
        )
        return False
    return True


def validate_portfolio_backtest_executor_input(
    data: pd.DataFrame, logger: Loggable
) -> bool:
    """
    Validate the input matrix for PortfolioBacktestExecutor.
    Returns True if valid, False otherwise.
    """
    if not isinstance(data, pd.DataFrame):
        logger.warning(f"Validation failed: Not a DataFrame. Value: {data}")
        return False
    if data.empty:
        logger.warning("Validation failed: DataFrame is empty.")
        return False
    # All columns must be numeric
    for col in data.columns:
        if not pd.api.types.is_numeric_dtype(data[col]):
            logger.warning(
                f"Validation failed: Column '{col}' not numeric. Dtype: {data[col].dtype}"
            )
            return False
    # Index should be unique
    if not data.index.is_unique:
        logger.warning("Validation failed: DataFrame index is not unique.")
        return False
    # Optionally, check for datetime index (common in time series)
    # Uncomment if you want to enforce this:
    # if not pd.api.types.is_datetime64_any_dtype(data.index):
    #     logger.warning("Validation failed: DataFrame index is not datetime.")
    #     return False
    return True
