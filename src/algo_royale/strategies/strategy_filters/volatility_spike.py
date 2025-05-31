import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def volatility_spike(row, range_col, volatility_col):
    """
    Returns True if the current price range is greater than the volatility measure,
    indicating a volatility spike.

    Args:
        row (pd.Series): A row of data.
        range_col (str): Column name for the price range.
        volatility_col (str): Column name for the volatility value.

    Returns:
        bool: True if range is greater than volatility, else False.
    """
    return row[range_col] > row[volatility_col]


class VolatilitySpikeFilter(StrategyFilter):
    """Filter to check for a volatility spike.
    This filter checks if the current price range exceeds a volatility measure,
    indicating a significant price movement.

    Args:
        range_col (str): Column name for the price range.
        volatility_col (str): Column name for the volatility value.

    Returns:
        pd.Series: Boolean Series where True indicates a volatility spike.

    Usage:
        filter = VolatilitySpikeFilter(range_col='Range', volatility_col='Volatility')
        df['volatility_spike'] = filter.apply(df)
    """

    def __init__(self, range_col: str, volatility_col: str):
        self.range_col = range_col
        self.volatility_col = volatility_col

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: volatility_spike(row, self.range_col, self.volatility_col),
            axis=1,
        )
