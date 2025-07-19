import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class TrailingStopExitCondition(StrategyCondition):
    """
    Exit when price falls below the trailing stop level.
    The trailing stop is calculated as the highest close since entry minus stop_pct.
    """

    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        stop_pct=0.02,
        debug: bool = False,
    ):
        super().__init__(close_col=close_col, stop_pct=stop_pct, debug=debug)
        self.close_col = close_col
        self.stop_pct = stop_pct

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        # Calculate the rolling maximum close (trailing high)
        trailing_high = df[self.close_col].cummax()
        trailing_stop = trailing_high * (1 - self.stop_pct)
        # Exit when price falls below trailing stop
        return df[self.close_col] < trailing_stop

    @property
    def required_columns(self):
        return [self.close_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
            "stop_pct": [0.01, 0.02, 0.03, 0.05],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
            stop_pct=trial.suggest_float(f"{prefix}stop_pct", 0.01, 0.05),
        )
