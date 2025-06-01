import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


@staticmethod
def volatility_spike(
    row,
    range_col: StrategyColumns = StrategyColumns.RANGE,
    volatility_col: StrategyColumns = StrategyColumns.VOLATILITY,
):
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


class VolatilitySpikeCondition(StrategyCondition):
    """Condition to check for a volatility spike.
    This condition checks if the current price range is greater than a specified volatility measure,
    indicating a significant price movement or volatility spike.

    Args:
        range_col (str): Column name for the price range.
        volatility_col (str): Column name for the volatility value.

    Returns:
        pd.Series: Boolean Series where True indicates a volatility spike.

    Usage:
        filter = VolatilitySpikeFilter(range_col='Range', volatility_col='Volatility')
        df['volatility_spike'] = filter.apply(df)
    """

    def __init__(
        self,
        range_col: StrategyColumns = StrategyColumns.RANGE,
        volatility_col: StrategyColumns = StrategyColumns.VOLATILITY,
    ):
        self.range_col = range_col
        self.volatility_col = volatility_col

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: volatility_spike(row, self.range_col, self.volatility_col),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.range_col, self.volatility_col]
