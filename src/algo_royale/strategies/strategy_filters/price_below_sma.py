import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def price_below_sma(row, sma_col, close_col):
    """
    Returns True if the price is below the SMA (indicating downtrend),
    else False.

    Args:
        row (pd.Series): A row of data.
        sma_col (str): Column name for SMA.
        close_col (str): Column name for close price.

    Returns:
        bool: True if price < SMA, else False.
    """
    return row[close_col] < row[sma_col]


class PriceBelowSMAFilter(StrategyFilter):
    """Filter to check if the price is below the Simple Moving Average (SMA).
    This filter checks if the current price is below the SMA, indicating a potential downtrend.

    Args:
        close_col (str): Column name for the close price.
        sma_col (str): Column name for the SMA values.

    Returns:
        pd.Series: Boolean Series where True indicates the price is below the SMA.

    Usage:
        filter = PriceBelowSMAFilter(close_col='Close', sma_col='SMA_50')
        df['price_below_sma'] = filter.apply(df)
    """

    def __init__(self, close_col: str, sma_col: str):
        self.close_col = close_col
        self.sma_col = sma_col

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: price_below_sma(row, self.sma_col, self.close_col),
            axis=1,
        )
