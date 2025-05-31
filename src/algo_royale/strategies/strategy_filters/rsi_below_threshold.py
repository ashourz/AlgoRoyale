import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def rsi_below_threshold(row, rsi_col, close_col, threshold=30):
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


class RSIBelowThresholdFilter(StrategyFilter):
    """Filter to check if the RSI value is below a specified threshold.
    This indicates oversold conditions, which may suggest a potential price reversal.

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

    def __init__(self, rsi_col: str, close_col: str, threshold: float = 30):
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
