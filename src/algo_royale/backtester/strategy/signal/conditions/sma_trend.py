import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class SMATrendCondition(StrategyCondition):
    """
    Simple Moving Average (SMA) Trend Condition
    Checks if the fast SMA is above the slow SMA.
    Parameters:
    - sma_fast_col: Column name for the fast SMA.
    - sma_slow_col: Column name for the slow SMA.
    """

    def __init__(
        self,
        sma_fast_col: SignalStrategyColumns = SignalStrategyColumns.SMA_50,
        sma_slow_col: SignalStrategyColumns = SignalStrategyColumns.SMA_200,
    ):
        super().__init__(
            sma_fast_col=sma_fast_col,
            sma_slow_col=sma_slow_col,
        )
        self.sma_fast_col = sma_fast_col
        self.sma_slow_col = sma_slow_col

    @property
    def required_columns(self):
        return [self.sma_fast_col, self.sma_slow_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.sma_fast_col] > df[self.sma_slow_col]

    def __call__(self, df: pd.DataFrame) -> pd.Series:
        return self.apply(df)

    @classmethod
    def available_param_grid(cls) -> dict:
        fast_periods = [10, 20, 50, 100]
        slow_periods = [100, 150, 200]
        fast_cols = [getattr(SignalStrategyColumns, f"SMA_{p}") for p in fast_periods]
        slow_cols = [getattr(SignalStrategyColumns, f"SMA_{p}") for p in slow_periods]
        # Only allow pairs where fast < slow
        valid_fast_cols = []
        valid_slow_cols = []
        for fp, fast in zip(fast_periods, fast_cols):
            for sp, slow in zip(slow_periods, slow_cols):
                if fp < sp:
                    valid_fast_cols.append(fast)
                    valid_slow_cols.append(slow)
        return {
            "sma_fast_col": valid_fast_cols,
            "sma_slow_col": valid_slow_cols,
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            sma_fast_col=trial.suggest_categorical(
                f"{prefix}sma_fast_col",
                [
                    SignalStrategyColumns.SMA_10,
                    SignalStrategyColumns.SMA_20,
                    SignalStrategyColumns.SMA_50,
                    SignalStrategyColumns.SMA_100,
                ],
            ),
            sma_slow_col=trial.suggest_categorical(
                f"{prefix}sma_slow_col",
                [
                    SignalStrategyColumns.SMA_100,
                    SignalStrategyColumns.SMA_150,
                    SignalStrategyColumns.SMA_200,
                ],
            ),
        )
