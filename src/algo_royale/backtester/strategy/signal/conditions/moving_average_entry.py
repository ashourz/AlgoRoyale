import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class MovingAverageEntryCondition(StrategyCondition):
    """
    Entry condition based on a moving average crossover strategy.
    This condition generates a signal when a short-term moving average crosses above
    a long-term moving average, indicating a potential bullish trend.
    Args:
        close_col (str): Column name for the close price.
        short_window (int): Window size for the short moving average.
        long_window (int): Window size for the long moving average.
    Returns:
        pd.Series: Boolean Series where True indicates a buy signal based on the moving average crossover.
    """

    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        short_window: int = 50,
        long_window: int = 200,
        logger: Loggable = None,
    ):
        super().__init__(
            close_col=close_col,
            short_window=short_window,
            long_window=long_window,
            logger=logger,
        )
        self.close_col = close_col
        self.short_window = short_window
        self.long_window = long_window

    @property
    def required_columns(self):
        return [self.close_col]

    @property
    def window_size(self) -> int:
        """Override to specify the window size for moving average crossover logic."""
        return max(
            self.short_window if self.short_window is not None else 1,
            self.long_window if self.long_window is not None else 1,
        )

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        short_ma = (
            df[self.close_col]
            .rolling(window=self.short_window, min_periods=self.short_window)
            .mean()
        )
        long_ma = (
            df[self.close_col]
            .rolling(window=self.long_window, min_periods=self.long_window)
            .mean()
        )
        # Golden Cross: short_ma crosses above long_ma
        signal_state = pd.Series(0, index=df.index)
        signal_state.loc[short_ma > long_ma] = 1
        signal_state.loc[short_ma < long_ma] = -1
        golden_cross = (signal_state == 1) & (signal_state.shift(1) != 1)
        return golden_cross

    @classmethod
    def available_param_grid(cls) -> dict:
        short_windows = [5, 10, 15, 20, 50]
        long_windows = [30, 50, 100, 200]
        valid_pairs = [
            (short, long)
            for short in short_windows
            for long in long_windows
            if short < long
        ]
        return {
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
            "short_window": [pair[0] for pair in valid_pairs],
            "long_window": [pair[1] for pair in valid_pairs],
        }

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix: str = ""):
        return cls(
            logger=logger,
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
            short_window=trial.suggest_int(f"{prefix}short_window", 5, 50),
            long_window=trial.suggest_int(f"{prefix}long_window", 30, 200),
        )
