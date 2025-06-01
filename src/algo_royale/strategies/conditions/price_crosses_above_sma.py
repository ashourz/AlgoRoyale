import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


@staticmethod
def price_crosses_above_sma(
    current_row,
    prev_row,
    sma_col: StrategyColumns = StrategyColumns.SMA_20,
    close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
):
    """
    Returns True if the price crosses above the SMA between the previous and current rows.
    This indicates a potential shift into an uptrend.

    Args:
        current_row (pd.Series): Current row of data.
        prev_row (pd.Series): Previous row of data.
        sma_col (str): Column name for the SMA values.
        close_col (str): Column name for the close price.

    Returns:
        bool: True if price crosses above SMA, else False.
    """
    return (
        prev_row[close_col] <= prev_row[sma_col]
        and current_row[close_col] > current_row[sma_col]
    )


class PriceCrossesAboveSMACondition(StrategyCondition):
    """Condition to check if the price crosses above a Simple Moving Average (SMA).
    This condition checks if the current price crosses above the SMA,
    indicating a potential bullish trend. It is typically used in trend-following strategies
    to identify potential buy signals when the price is above the SMA.
    This condition is applied to each row of a DataFrame containing price and SMA values.
    This condition is useful for strategies that require the price to cross above a certain SMA
    to enter trades.

    Args:
        close_col (StrategyColumns): Column name for the close price.
        sma_col (StrategyColumns): Column name for the SMA values.

    Returns:
        pd.Series: Boolean Series where True indicates the price crosses above the SMA.

    Usage:
        filter = PriceCrossesAboveSMAFilter(close_col='Close', sma_col='SMA_50')
        df['price_crosses_above_sma'] = filter.apply(df)
    """

    def __init__(
        self,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        sma_col: StrategyColumns = StrategyColumns.SMA_20,
    ):
        self.close_col = close_col
        self.sma_col = sma_col

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: price_crosses_above_sma(
                row, df.shift(1).loc[row.name], self.sma_col, self.close_col
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.close_col, self.sma_col]
