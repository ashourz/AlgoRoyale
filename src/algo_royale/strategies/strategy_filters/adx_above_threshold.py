import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def adx_above_threshold(row, adx_col, close_col, threshold=25):
    """
    Returns True if the ADX value is above a threshold (indicating strong trend).

    Args:
        row (pd.Series): A row of data.
        adx_col (str): Column name for ADX.
        close_col (str): Column name for close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        bool: True if ADX > threshold, else False.
    """
    return row[adx_col] > threshold


class ADXAboveThresholdFilter(StrategyFilter):
    """Filter to check if the ADX value is above a specified threshold.
    This indicates a strong trend environment, which may be suitable for trend-following strategies.

    Args:
        adx_col (str): Column name for the ADX values.
        close_col (str): Column name for the close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        pd.Series: Boolean Series where True indicates ADX is above the threshold.

    Usage:
        filter = ADXAboveThresholdFilter(adx_col='ADX', close_col='Close', threshold=25)
        df['adx_above_threshold'] = filter.apply(df)
    """

    def __init__(self, adx_col: str, close_col: str, threshold: float = 25):
        self.adx_col = adx_col
        self.close_col = close_col
        self.threshold = threshold

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: adx_above_threshold(
                row, self.adx_col, self.close_col, self.threshold
            ),
            axis=1,
        )
