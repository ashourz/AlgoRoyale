import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import StrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def volatility_spike(
    row,
    range_col: StrategyColumns = StrategyColumns.RANGE,
    volatility_col: StrategyColumns = StrategyColumns.VOLATILITY_10,
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
        volatility_col: StrategyColumns = StrategyColumns.VOLATILITY_10,
    ):
        super().__init__(
            range_col=range_col,
            volatility_col=volatility_col,
        )
        self.range_col = range_col
        self.volatility_col = volatility_col

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: volatility_spike(row, self.range_col, self.volatility_col),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.range_col, self.volatility_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "range_col": [
                StrategyColumns.RANGE,
                StrategyColumns.ATR_14,
            ],
            "volatility_col": [
                StrategyColumns.VOLATILITY_10,
                StrategyColumns.VOLATILITY_20,
                StrategyColumns.VOLATILITY_50,
                StrategyColumns.HIST_VOLATILITY_20,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            range_col=trial.suggest_categorical(
                prefix + "range_col",
                [
                    StrategyColumns.RANGE,
                    StrategyColumns.ATR_14,
                ],
            ),
            volatility_col=trial.suggest_categorical(
                prefix + "volatility_col",
                [
                    StrategyColumns.VOLATILITY_10,
                    StrategyColumns.VOLATILITY_20,
                    StrategyColumns.VOLATILITY_50,
                    StrategyColumns.HIST_VOLATILITY_20,
                ],
            ),
        )
