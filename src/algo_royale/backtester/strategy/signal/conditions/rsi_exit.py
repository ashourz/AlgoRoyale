import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.logging.loggable import Loggable


class RSIExitCondition(StrategyCondition):
    def __init__(
        self,
        close_col=SignalStrategyColumns.CLOSE_PRICE,
        period=14,
        overbought=70,
        logger: Loggable = None,
    ):
        super().__init__(
            close_col=close_col, period=period, overbought=overbought, logger=logger
        )
        self.close_col = close_col
        self.period = period
        self.overbought = overbought

    @property
    def required_columns(self):
        return [self.close_col]

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        delta = df[self.close_col].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=self.period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=self.period - 1, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi > self.overbought

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "close_col": [
                SignalStrategyColumns.CLOSE_PRICE,
                SignalStrategyColumns.OPEN_PRICE,
            ],
            "period": [5, 10, 14, 20, 30],
            "overbought": [60, 65, 70, 75, 80],
        }

    @classmethod
    def optuna_suggest(cls, logger: Loggable, trial: Trial, prefix=""):
        return cls(
            logger=logger,
            close_col=trial.suggest_categorical(
                f"{prefix}close_col",
                [SignalStrategyColumns.CLOSE_PRICE, SignalStrategyColumns.OPEN_PRICE],
            ),
            period=trial.suggest_int(f"{prefix}period", 5, 30),
            overbought=trial.suggest_int(f"{prefix}overbought", 60, 80),
        )
