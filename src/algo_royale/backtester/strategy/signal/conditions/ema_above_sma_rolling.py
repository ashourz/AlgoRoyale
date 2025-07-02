import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class EMAAboveSMARollingCondition(StrategyCondition):
    """
    Condition that checks if the EMA is above the SMA and rising for a rolling window.
    True when EMA > SMA and EMA is increasing for the specified window.
    """

    def __init__(
        self,
        ema_col=SignalStrategyColumns.EMA_20,
        sma_col=SignalStrategyColumns.SMA_50,
        window: int = 3,
    ):
        super().__init__(ema_col=ema_col, sma_col=sma_col, window=window)
        self.ema_col = ema_col
        self.sma_col = sma_col
        self.window = window

    @property
    def required_columns(self):
        return [self.ema_col, self.sma_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        trend = (df[self.ema_col] > df[self.sma_col]) & (
            df[self.ema_col] > df[self.ema_col].shift(1)
        )
        return trend.rolling(window=self.window).sum() == self.window

    @classmethod
    def available_param_grid(cls) -> dict:
        ema_periods = [9, 10, 12, 20, 26, 50, 100, 150, 200]
        sma_periods = [10, 20, 50, 100, 150, 200]
        ema_cols = [getattr(SignalStrategyColumns, f"EMA_{p}") for p in ema_periods]
        sma_cols = [getattr(SignalStrategyColumns, f"SMA_{p}") for p in sma_periods]

        return {
            "ema_col": ema_cols,
            "sma_col": sma_cols,
            "window": [2, 3, 5, 7, 10, 15, 20],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            ema_col=trial.suggest_categorical(
                f"{prefix}ema_col",
                cls.available_param_grid()["ema_col"],
            ),
            sma_col=trial.suggest_categorical(
                f"{prefix}sma_col",
                cls.available_param_grid()["sma_col"],
            ),
            window=trial.suggest_int(f"{prefix}window", 2, 20),
        )
