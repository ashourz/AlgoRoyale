import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def adx_below_threshold(row, adx_col, threshold=25):
    """
    Returns True if the ADX value is below a specified threshold,
    indicating a weak or no trend environment.

    Args:
        row (pd.Series): A row of data.
        adx_col (str): Column name for the ADX values.
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        bool: True if ADX is below threshold, else False.
    """
    return row[adx_col] < threshold


class ADXBelowThresholdFilter(StrategyFilter):
    """Filter to check if the ADX value is below a specified threshold.
    This indicates a weak or no trend environment, which may not be suitable for trend-following strategies.

    Args:
        adx_col (str): Column name for the ADX values.
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        pd.Series: Boolean Series where True indicates ADX is below the threshold.

    Usage:
        filter = ADXBelowThresholdFilter(adx_col='ADX', threshold=25)
        df['adx_below_threshold'] = filter.apply(df)
    """

    def __init__(self, adx_col: str, threshold: float = 25):
        self.adx_col = adx_col
        self.threshold = threshold

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.adx_col] < self.threshold
