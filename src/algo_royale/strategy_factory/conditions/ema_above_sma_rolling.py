import pandas as pd
from optuna import Trial

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class EMAAboveSMARollingCondition(StrategyCondition):
    """
    Condition that checks if the EMA is above the SMA and rising for a rolling window.
    True when EMA > SMA and EMA is increasing for the specified window.
    """

    def __init__(
        self,
        ema_sma_pair: tuple[StrategyColumns, StrategyColumns] = (
            StrategyColumns.EMA_20,
            StrategyColumns.SMA_50,
        ),
        window: int = 3,
    ):
        super().__init__(ema_sma_pair=ema_sma_pair, window=window)
        self.ema_col, self.sma_col = ema_sma_pair
        self.window = window

    @property
    def required_columns(self):
        return {self.ema_col, self.sma_col}

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        trend = (df[self.ema_col] > df[self.sma_col]) & (
            df[self.ema_col] > df[self.ema_col].shift(1)
        )
        return trend.rolling(window=self.window).sum() == self.window

    @classmethod
    def available_param_grid(cls) -> dict:
        ema_periods = [9, 10, 12, 20, 26, 50, 100, 150, 200]
        sma_periods = [10, 20, 50, 100, 150, 200]
        ema_cols = [getattr(StrategyColumns, f"EMA_{p}") for p in ema_periods]
        sma_cols = [getattr(StrategyColumns, f"SMA_{p}") for p in sma_periods]

        # Only allow pairs where EMA period < SMA period
        pairs = [
            (ema, sma)
            for ema, ep in zip(ema_cols, ema_periods)
            for sma, sp in zip(sma_cols, sma_periods)
            if ep < sp
        ]

        return {
            "ema_sma_pair": pairs,
            "window": [2, 3, 5, 7, 10, 15, 20],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            ema_sma_pair=trial.suggest_categorical(
                f"{prefix}ema_sma_pair",
                cls.available_param_grid()["ema_sma_pair"],
            ),
            window=trial.suggest_int(f"{prefix}window", 2, 20),
        )
