import pandas as pd
from optuna import Trial

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


class VolatilityBreakoutEntryCondition(StrategyCondition):
    """Condition to identify volatility breakout entry points in a trading strategy.
    This condition checks if the price range exceeds a specified threshold relative to the 20-period volatility,"""

    def __init__(
        self,
        threshold=1.5,
        sma_col: StrategyColumns = StrategyColumns.SMA_20,
        volatility_col: StrategyColumns = StrategyColumns.VOLATILITY_20,
        range_col: StrategyColumns = StrategyColumns.RANGE,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
    ):
        super().__init__(
            threshold=threshold,
            sma_col=sma_col,
            volatility_col=volatility_col,
            range_col=range_col,
            close_col=close_col,
        )
        self.threshold = threshold
        self.sma_col = sma_col
        self.close_col = volatility_col
        self.range_col = range_col
        self.close_col = close_col

    @property
    def required_columns(self):
        return [
            self.close_col,
            self.range_col,
            self.close_col,
            self.sma_col,
        ]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        breakout = df[self.range_col] > self.threshold * df[self.volatility_col]
        uptrend = df[StrategyColumns.CLOSE_PRICE] > df[self.sma_col]
        return breakout & uptrend

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "threshold": [0.8, 1.0, 1.2, 1.5, 2.0, 2.5],
            "sma_col": [
                StrategyColumns.SMA_10,
                StrategyColumns.SMA_20,
                StrategyColumns.SMA_50,
                StrategyColumns.SMA_100,
                StrategyColumns.SMA_150,
                StrategyColumns.SMA_200,
            ],
            "volatility_col": [
                StrategyColumns.VOLATILITY_10,
                StrategyColumns.VOLATILITY_20,
                StrategyColumns.VOLATILITY_50,
                StrategyColumns.HIST_VOLATILITY_20,
            ],
            "range_col": [
                StrategyColumns.RANGE,
                StrategyColumns.ATR_14,
                # Add other range columns if available
            ],
            "close_col": [
                StrategyColumns.CLOSE_PRICE,
                StrategyColumns.OPEN_PRICE,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            threshold=trial.suggest_float(f"{prefix}threshold", 0.8, 2.5),
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
            volatility_col=trial.suggest_categorical(
                f"{prefix}volatility_col",
                [
                    StrategyColumns.VOLATILITY_10,
                    StrategyColumns.VOLATILITY_20,
                    StrategyColumns.VOLATILITY_50,
                    StrategyColumns.HIST_VOLATILITY_20,
                ],
            ),
            range_col=trial.suggest_categorical(
                f"{prefix}range_col",
                [
                    StrategyColumns.RANGE,
                    StrategyColumns.ATR_14,
                    # Add other range columns if available
                ],
            ),
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [
                    StrategyColumns.CLOSE_PRICE,
                    StrategyColumns.OPEN_PRICE,
                ],
            ),
        )
