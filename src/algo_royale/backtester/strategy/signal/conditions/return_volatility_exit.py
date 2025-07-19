import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


class ReturnVolatilityExitCondition(StrategyCondition):
    """
    Exit condition based on return and volatility.
    Triggers when:
    - The return is below a specified threshold, OR
    - The price range exceeds a specified volatility measure.

    """

    def __init__(
        self,
        threshold: float,
        return_col=SignalStrategyColumns.PCT_RETURN,  # or LOG_RETURN
        range_col: SignalStrategyColumns = SignalStrategyColumns.RANGE,
        volatility_col: SignalStrategyColumns = SignalStrategyColumns.VOLATILITY_20,
        debug: bool = False,
    ):
        super().__init__(
            return_col=return_col,
            range_col=range_col,
            volatility_col=volatility_col,
            threshold=threshold,
            debug=debug,
        )
        self.return_col = return_col
        self.range_col = range_col
        self.volatility_col = volatility_col
        self.threshold = threshold

    @property
    def required_columns(self):
        return [self.return_col, self.range_col, self.volatility_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        weakness = df[self.return_col] < self.threshold
        volatility_spike = df[self.range_col] > df[self.volatility_col]
        return weakness | volatility_spike

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "threshold": [-0.005, -0.01, -0.02, -0.03, -0.04, -0.05, -0.06, -0.1],
            "return_col": [
                SignalStrategyColumns.PCT_RETURN,
                SignalStrategyColumns.LOG_RETURN,
            ],
            "range_col": [SignalStrategyColumns.RANGE, SignalStrategyColumns.ATR_14],
            "volatility_col": [
                SignalStrategyColumns.HIST_VOLATILITY_20,
                SignalStrategyColumns.VOLATILITY_10,
                SignalStrategyColumns.VOLATILITY_20,
                SignalStrategyColumns.VOLATILITY_50,
            ],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix=""):
        return cls(
            threshold=trial.suggest_float(f"{prefix}threshold", -0.1, -0.005),
            return_col=trial.suggest_categorical(
                f"{prefix}return_col",
                [SignalStrategyColumns.PCT_RETURN, SignalStrategyColumns.LOG_RETURN],
            ),
            range_col=trial.suggest_categorical(
                f"{prefix}range_col",
                [SignalStrategyColumns.RANGE, SignalStrategyColumns.ATR_14],
            ),
            volatility_col=trial.suggest_categorical(
                f"{prefix}volatility_col",
                [
                    SignalStrategyColumns.HIST_VOLATILITY_20,
                    SignalStrategyColumns.VOLATILITY_10,
                    SignalStrategyColumns.VOLATILITY_20,
                    SignalStrategyColumns.VOLATILITY_50,
                ],
            ),
        )
