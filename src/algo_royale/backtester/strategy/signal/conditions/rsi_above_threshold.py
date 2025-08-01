import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


@staticmethod
def rsi_above_threshold(
    row, rsi_col: SignalStrategyColumns = SignalStrategyColumns.RSI, threshold=70
):
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


class RSIAboveThresholdCondition(StrategyCondition):
    """Condition to check if RSI is above a specified threshold.
    This condition checks if the Relative Strength Index (RSI) is above a specified threshold,
    indicating overbought conditions. It is typically used in mean-reversion strategies
    to identify potential sell signals when the market is overbought.
    This condition is applied to each row of a DataFrame containing RSI values.
    This condition is useful for strategies that require the RSI to be above a certain threshold
    to enter trades.

    Args:
        rsi_col (StrategyColumns): Column name for the RSI values.
        threshold (float, optional): Threshold value. Default is 70.

    Returns:
        pd.Series: Boolean Series where True indicates RSI is above the threshold.

    Usage:
        filter = RSIAboveThresholdFilter(rsi_col='RSI', threshold=70)
        df['rsi_above_threshold'] = filter.apply(df)
    """

    def __init__(
        self,
        rsi_col: SignalStrategyColumns = SignalStrategyColumns.RSI,
        threshold: float = 70,
        logger: Loggable = None,
    ):
        super().__init__(rsi_col=rsi_col, threshold=threshold, logger=logger)
        self.rsi_col = rsi_col
        self.threshold = threshold

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: rsi_above_threshold(row, self.rsi_col, self.threshold),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.rsi_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "rsi_col": [SignalStrategyColumns.RSI],
            "threshold": [50, 55, 60, 65, 70, 75, 80, 85],
        }

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix=""):
        return cls(
            logger=logger,
            rsi_col=SignalStrategyColumns.RSI,
            threshold=trial.suggest_int(f"{prefix}threshold", 50, 85),
        )
