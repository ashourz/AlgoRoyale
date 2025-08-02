import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class VolatilityBreakoutEntryCondition(StrategyCondition):
    """Condition to identify volatility breakout entry points in a trading strategy.
    This condition checks if the price range exceeds a specified threshold relative to the 20-period volatility,"""

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

    @property
    def window_size(self) -> int:
        """Override to specify the window size for volatility calculation."""
        try:
            # Extract period from column names, e.g., 'VOLATILITY_20' -> 20
            volatility_window = int(str(self.volatility_col).split("_")[-1])
            sma_window = int(str(self.sma_col).split("_")[-1])
            return max(volatility_window, sma_window)
        except (ValueError, IndexError):
            self.logger.error(
                f"Failed to parse periods from columns: {self.volatility_col}, {self.sma_col}. "
                "Defaulting to 0."
            )
            return 0

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        breakout = df[self.range_col] > self.threshold * df[self.volatility_col]
        uptrend = df[SignalStrategyColumns.CLOSE_PRICE] > df[self.sma_col]
        return breakout & uptrend

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
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix=""):
        return cls(
            logger=logger,
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
                [
                    SignalStrategyColumns.CLOSE_PRICE,
                    SignalStrategyColumns.OPEN_PRICE,
                ],
            ),
        )
