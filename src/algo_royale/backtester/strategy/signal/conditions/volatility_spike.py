import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


@staticmethod
def volatility_spike(
    row,
    range_col: SignalStrategyColumns = SignalStrategyColumns.RANGE,
    volatility_col: SignalStrategyColumns = SignalStrategyColumns.VOLATILITY_10,
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
        range_col: SignalStrategyColumns = SignalStrategyColumns.RANGE,
        volatility_col: SignalStrategyColumns = SignalStrategyColumns.VOLATILITY_10,
        logger: Loggable = None,
    ):
        super().__init__(
            range_col=range_col,
            volatility_col=volatility_col,
            logger=logger,
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

    @property
    def window_size(self) -> int:
        """Override to specify the window size for volatility calculation."""
        try:
            # Extract period from column names, e.g., 'VOLATILITY_10' -> 10
            return int(str(self.volatility_col).split("_")[-1])
        except (ValueError, IndexError):
            self.logger.error(
                f"Failed to parse volatility period from column: {self.volatility_col}. Defaulting to 0."
            )
            return 0

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "range_col": [
                SignalStrategyColumns.RANGE,
                SignalStrategyColumns.ATR_14,
            ],
            "volatility_col": [
                SignalStrategyColumns.VOLATILITY_10,
                SignalStrategyColumns.VOLATILITY_20,
                SignalStrategyColumns.VOLATILITY_50,
                SignalStrategyColumns.HIST_VOLATILITY_20,
            ],
        }

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix=""):
        return cls(
            logger=logger,
            range_col=trial.suggest_categorical(
                prefix + "range_col",
                [
                    SignalStrategyColumns.RANGE,
                    SignalStrategyColumns.ATR_14,
                ],
            ),
            volatility_col=trial.suggest_categorical(
                prefix + "volatility_col",
                [
                    SignalStrategyColumns.VOLATILITY_10,
                    SignalStrategyColumns.VOLATILITY_20,
                    SignalStrategyColumns.VOLATILITY_50,
                    SignalStrategyColumns.HIST_VOLATILITY_20,
                ],
            ),
        )
