import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import StrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def adx_below_threshold(
    row, adx_col: StrategyColumns = StrategyColumns.ADX, threshold=25
):
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


class ADXBelowThresholdCondition(StrategyCondition):
    """Condition to check if ADX is below a specified threshold.
    This condition checks if the Average Directional Index (ADX) is below a specified threshold,
    indicating a weak or no trend in the market. This is typically used to filter out periods
    of low volatility or sideways movement in trend-following strategies.
    This indicates a weak or no trend environment, which may not be suitable for trend-following strategies.

    Args:
        adx_col (StrategyColumns): Column name for the ADX values.
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        pd.Series: Boolean Series where True indicates ADX is below the threshold.

    Usage:
        filter = ADXBelowThresholdFilter(adx_col='ADX', threshold=25)
        df['adx_below_threshold'] = filter.apply(df)
    """

    def __init__(
        self, adx_col: StrategyColumns = StrategyColumns.ADX, threshold: float = 25
    ):
        super().__init__(adx_col=adx_col, threshold=threshold)
        self.adx_col = adx_col
        self.threshold = threshold

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.adx_col] < self.threshold

    @property
    def required_columns(self):
        return [self.adx_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "adx_col": [StrategyColumns.ADX],
            "threshold": [10, 15, 20, 25, 30, 35, 40],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            adx_col=trial.suggest_categorical(
                f"{prefix}adx_col", [StrategyColumns.ADX]
            ),
            threshold=trial.suggest_int(f"{prefix}threshold", 10, 40),
        )
