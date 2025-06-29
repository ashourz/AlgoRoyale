import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import StrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class TrendAboveSMACondition(StrategyCondition):
    def __init__(
        self,
        price_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        sma_col: StrategyColumns = StrategyColumns.SMA_20,
    ):
        super().__init__(price_col=price_col, sma_col=sma_col)
        self.price_col = price_col
        self.sma_col = sma_col

    @property
    def required_columns(self):
        return [self.price_col, self.sma_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.price_col] > df[self.sma_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "price_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            "sma_col": [
                StrategyColumns.SMA_10,
                StrategyColumns.SMA_20,
                StrategyColumns.SMA_50,
                StrategyColumns.SMA_100,
                StrategyColumns.SMA_150,
                StrategyColumns.SMA_200,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            price_col=trial.suggest_categorical(
                f"{prefix}price_col",
                [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
            ),
            sma_col=trial.suggest_categorical(
                f"{prefix}sma_col",
                [
                    StrategyColumns.SMA_10,
                    StrategyColumns.SMA_20,
                    StrategyColumns.SMA_50,
                    StrategyColumns.SMA_100,
                    StrategyColumns.SMA_150,
                    StrategyColumns.SMA_200,
                ],
            ),
        )
