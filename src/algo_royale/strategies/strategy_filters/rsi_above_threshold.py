import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def rsi_above_threshold(row, rsi_col, threshold=70):
    """
    Returns True if the RSI value is above a specified threshold,
    indicating overbought conditions.

    Args:
        row (pd.Series): A row of data.
        rsi_col (str): Column name for RSI values.
        threshold (float, optional): Threshold value. Default is 70.

    Returns:
        bool: True if RSI is above threshold, else False.
    """
    return row[rsi_col] > threshold


class RSIAboveThresholdFilter(StrategyFilter):
    """Filter to check if the RSI value is above a specified threshold.
    This indicates overbought conditions, which may suggest a potential price reversal.

    Args:
        rsi_col (str): Column name for the RSI values.
        threshold (float, optional): Threshold value. Default is 70.

    Returns:
        pd.Series: Boolean Series where True indicates RSI is above the threshold.

    Usage:
        filter = RSIAboveThresholdFilter(rsi_col='RSI', threshold=70)
        df['rsi_above_threshold'] = filter.apply(df)
    """

    def __init__(self, rsi_col: str, threshold: float = 70):
        self.rsi_col = rsi_col
        self.threshold = threshold

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: rsi_above_threshold(row, self.rsi_col, self.threshold),
            axis=1,
        )
