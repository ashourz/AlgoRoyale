import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class PullbackEntryCondition(StrategyCondition):
    def __init__(
        self,
        ma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
    ):
        super().__init__(ma_col=ma_col, close_col=close_col)
        self.ma_col = ma_col
        self.close_col = close_col

    @property
    def required_columns(self):
        return [self.ma_col, self.close_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        above_ma = df[self.close_col] > df[self.ma_col]
        below_ma_yesterday = df[self.close_col].shift(1) < df[self.ma_col].shift(1)
        return above_ma & below_ma_yesterday

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "ma_col": [
                SignalStrategyColumns.SMA_10,
                SignalStrategyColumns.SMA_20,
                SignalStrategyColumns.SMA_50,
                SignalStrategyColumns.SMA_100,
                SignalStrategyColumns.SMA_150,
                SignalStrategyColumns.SMA_200,
                SignalStrategyColumns.EMA_9,
                SignalStrategyColumns.EMA_10,
                SignalStrategyColumns.EMA_20,
                SignalStrategyColumns.EMA_26,
                SignalStrategyColumns.EMA_50,
                SignalStrategyColumns.EMA_100,
                SignalStrategyColumns.EMA_150,
                SignalStrategyColumns.EMA_200,
            ],
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            ma_col=trial.suggest_categorical(
                f"{prefix}ma_col",
                [
                    SignalStrategyColumns.SMA_10,
                    SignalStrategyColumns.SMA_20,
                    SignalStrategyColumns.SMA_50,
                    SignalStrategyColumns.SMA_100,
                    SignalStrategyColumns.SMA_150,
                    SignalStrategyColumns.SMA_200,
                    SignalStrategyColumns.EMA_9,
                    SignalStrategyColumns.EMA_10,
                    SignalStrategyColumns.EMA_20,
                    SignalStrategyColumns.EMA_26,
                    SignalStrategyColumns.EMA_50,
                    SignalStrategyColumns.EMA_100,
                    SignalStrategyColumns.EMA_150,
                    SignalStrategyColumns.EMA_200,
                ],
            ),
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
        )
