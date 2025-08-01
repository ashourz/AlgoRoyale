import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class VolatilityBreakoutExitCondition(StrategyCondition):
    """Condition to identify volatility breakout exit points in a trading strategy.
    This condition checks if the price range exceeds a specified threshold relative to a volatility measure,
    and the price is below a moving average (downtrend).
    """

    def __init__(
        self,
        threshold=1.5,
        sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
        volatility_col: SignalStrategyColumns = SignalStrategyColumns.VOLATILITY_20,
        range_col: SignalStrategyColumns = SignalStrategyColumns.RANGE,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        logger: Loggable = None,
    ):
        super().__init__(
            threshold=threshold,
            sma_col=sma_col,
            volatility_col=volatility_col,
            range_col=range_col,
            close_col=close_col,
            logger=logger,
        )
        self.threshold = threshold
        self.sma_col = sma_col
        self.volatility_col = volatility_col
        self.range_col = range_col
        self.close_col = close_col

    @property
    def required_columns(self):
        return [
            self.volatility_col,
            self.range_col,
            self.close_col,
            self.sma_col,
        ]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        breakout = df[self.range_col] > self.threshold * df[self.volatility_col]
        downtrend = df[self.close_col] <= df[self.sma_col]
        return breakout & downtrend

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "threshold": [0.8, 1.0, 1.2, 1.5, 2.0, 2.5],
            "sma_col": [
                SignalStrategyColumns.SMA_10,
                SignalStrategyColumns.SMA_20,
                SignalStrategyColumns.SMA_50,
                SignalStrategyColumns.SMA_100,
                SignalStrategyColumns.SMA_150,
                SignalStrategyColumns.SMA_200,
            ],
            "volatility_col": [
                SignalStrategyColumns.VOLATILITY_10,
                SignalStrategyColumns.VOLATILITY_20,
                SignalStrategyColumns.VOLATILITY_50,
                SignalStrategyColumns.HIST_VOLATILITY_20,
            ],
            "range_col": [
                SignalStrategyColumns.RANGE,
                SignalStrategyColumns.ATR_14,
                # Add other range columns if available
            ],
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            threshold=trial.suggest_float(f"{prefix}threshold", 0.8, 2.5),
            sma_col=trial.suggest_categorical(
                f"{prefix}sma_col",
                [
                    SignalStrategyColumns.SMA_10,
                    SignalStrategyColumns.SMA_20,
                    SignalStrategyColumns.SMA_50,
                    SignalStrategyColumns.SMA_100,
                    SignalStrategyColumns.SMA_150,
                    SignalStrategyColumns.SMA_200,
                ],
            ),
            volatility_col=trial.suggest_categorical(
                f"{prefix}volatility_col",
                [
                    SignalStrategyColumns.VOLATILITY_10,
                    SignalStrategyColumns.VOLATILITY_20,
                    SignalStrategyColumns.VOLATILITY_50,
                    SignalStrategyColumns.HIST_VOLATILITY_20,
                ],
            ),
            range_col=trial.suggest_categorical(
                f"{prefix}range_col",
                [
                    SignalStrategyColumns.RANGE,
                    SignalStrategyColumns.ATR_14,
                    # Add other range columns if available
                ],
            ),
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
        )
