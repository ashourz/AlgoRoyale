import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def rsi_below_threshold(
    row,
    rsi_col: StrategyColumns = StrategyColumns.RSI,
    close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
    threshold=30,
):
    """
    Returns True if the RSI value is below a threshold (indicating oversold).
    Can be used as a contrarian filter.

    Args:
        row (pd.Series): A row of data.
        rsi_col (str): Column name for RSI.
        close_col (str): Column name for close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 30.

    Returns:
        bool: True if RSI < threshold, else False.
    """
    return row[rsi_col] < threshold


class RSIBelowThresholdConditin(StrategyCondition):
    """Condition to check if RSI is below a specified threshold.
    This condition checks if the Relative Strength Index (RSI) is below a specified threshold,
    indicating oversold conditions. It is typically used in contrarian strategies
    to identify potential buy signals when the market is oversold.
    This condition is applied to each row of a DataFrame containing RSI values.
    This condition is useful for strategies that require the RSI to be below a certain threshold
    to enter trades.

    Args:
        rsi_col (str): Column name for the RSI values.
        close_col (str): Column name for the close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 30.

    Returns:
        pd.Series: Boolean Series where True indicates RSI is below the threshold.

    Usage:
        filter = RSIBelowThresholdFilter(rsi_col='RSI', close_col='Close', threshold=30)
        df['rsi_below_threshold'] = filter.apply(df)
    """

    def __init__(
        self,
        rsi_col: StrategyColumns = StrategyColumns.RSI,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        threshold=30,
    ):
        self.rsi_col = rsi_col
        self.close_col = close_col
        self.threshold = threshold

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: rsi_below_threshold(
                row, self.rsi_col, self.close_col, self.threshold
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.rsi_col, self.close_col]

    @classmethod
    def available_param_grid(cls):
        return {
            "rsi_col": [StrategyColumns.RSI],
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            "threshold": [20, 25, 30, 35, 40, 45, 50],
        }
