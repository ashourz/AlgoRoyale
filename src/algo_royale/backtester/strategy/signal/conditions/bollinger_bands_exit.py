import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class BollingerBandsExitCondition(StrategyCondition):
    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        window=20,
        num_std=2,
        logger: Loggable = None,
    ):
        super().__init__(
            close_col=close_col, window=window, num_std=num_std, logger=logger
        )
        self.close_col = close_col
        self.window = window
        self.num_std = num_std

    @property
    def required_columns(self):
        return [self.close_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        rolling_mean = df[self.close_col].rolling(window=self.window).mean()
        rolling_std = df[self.close_col].rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        valid_idx = rolling_mean.notna()
        return valid_idx & (df[self.close_col] > upper_band)

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
            "window": [10, 20, 30],
            "num_std": [1, 2, 3],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
            window=trial.suggest_int(f"{prefix}window", 10, 30),
            num_std=trial.suggest_categorical(f"{prefix}num_std", [1, 2, 3]),
        )
