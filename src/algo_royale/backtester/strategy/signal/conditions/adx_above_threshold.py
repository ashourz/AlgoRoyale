from typing import Optional

import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


@staticmethod
def adx_above_threshold(
    row,
    adx_col: SignalStrategyColumns = SignalStrategyColumns.ADX,
    close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
    threshold=25,
):
    """
    Returns True if the ADX value is above a threshold (indicating strong trend).

    Args:
        row (pd.Series): A row of data.
        adx_col (StrategyColumns): Column name for the ADX values.
        close_col (StrategyColumns): Column name for the close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        bool: True if ADX > threshold, else False.
    """
    return row[adx_col] > threshold


class ADXAboveThresholdCondition(StrategyCondition):
    """Condition to check if ADX is above a specified threshold.
    This condition checks if the Average Directional Index (ADX) is above a specified threshold,
    indicating a strong trend in the market.
    This is typically used in trend-following strategies to filter out periods of low volatility.
    It is applied to each row of a DataFrame containing ADX values.
    This condition is useful for strategies that require a strong trend to enter trades.
    Args:
        adx_col (StrategyColumns): Column name for the ADX values.
        close_col (StrategyColumns): Column name for the close price (not used in logic but kept for uniformity).
        threshold (float, optional): Threshold value. Default is 25.

    Returns:
        pd.Series: Boolean Series where True indicates ADX is above the threshold.

    Usage:
        filter = ADXAboveThresholdFilter(adx_col='ADX', close_col='Close', threshold=25)
        df['adx_above_threshold'] = filter.apply(df)
    """

    def __init__(
        self,
        adx_col: SignalStrategyColumns = SignalStrategyColumns.ADX,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        threshold: float = 25,
        logger: Optional[Loggable] = None,
    ):
        super().__init__(
            adx_col=adx_col, close_col=close_col, threshold=threshold, logger=logger
        )
        self.adx_col = adx_col
        self.close_col = close_col
        self.threshold = threshold

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: adx_above_threshold(
                row, self.adx_col, self.close_col, self.threshold
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.adx_col, self.close_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "adx_col": [SignalStrategyColumns.ADX],
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.CLOSE,
            ],
            "threshold": [20, 25, 30, 35, 40, 45, 50],
        }

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix: str = ""):
        return cls(
            logger=logger,
            adx_col=trial.suggest_categorical(
                f"{prefix}adx_col", [SignalStrategyColumns.ADX]
            ),
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.CLOSE],
            ),
            threshold=trial.suggest_int(f"{prefix}threshold", 20, 50),
        )
