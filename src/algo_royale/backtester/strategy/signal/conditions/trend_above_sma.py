import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class TrendAboveSMACondition(StrategyCondition):
    def __init__(
        self,
        price_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
        logger: Loggable = None,
    ):
        super().__init__(price_col=price_col, sma_col=sma_col, logger=logger)
        self.price_col = price_col
        self.sma_col = sma_col

    @property
    def required_columns(self):
        return [self.price_col, self.sma_col]

    @property
    def window_size(self) -> int:
        """Override to specify the window size for SMA calculation."""
        try:
            # Extract period from column names, e.g., 'SMA_20' -> 20
            return int(str(self.sma_col).split("_")[-1])
        except (ValueError, IndexError):
            self.logger.error(
                f"Failed to parse SMA period from column: {self.sma_col}. Defaulting to 0."
            )
            return 0

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df[self.price_col] > df[self.sma_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "price_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
            "sma_col": [
                SignalStrategyColumns.SMA_10,
                SignalStrategyColumns.SMA_20,
                SignalStrategyColumns.SMA_50,
                SignalStrategyColumns.SMA_100,
                SignalStrategyColumns.SMA_150,
                SignalStrategyColumns.SMA_200,
            ],
        }

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix=""):
        return cls(
            logger=logger,
            price_col=trial.suggest_categorical(
                f"{prefix}price_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
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
        )
