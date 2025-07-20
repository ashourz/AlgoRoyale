import pandas as pd
from optuna import Trial

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def macd_bearish_cross(
    current_row,
    prev_row,
    macd_col: SignalStrategyColumns = SignalStrategyColumns.MACD,
    signal_col: SignalStrategyColumns = SignalStrategyColumns.MACD_SIGNAL,
):
    """
    Returns True if MACD crosses below its signal line between previous and current rows,
    indicating bearish momentum.

    Args:
        current_row (pd.Series): Current row of data.
        prev_row (pd.Series): Previous row of data.
        macd_col (str): Column name for the MACD values.
        signal_col (str): Column name for the MACD signal line values.

    Returns:
        bool: True if MACD crosses below signal line, else False.
    """
    return (
        prev_row[macd_col] >= prev_row[signal_col]
        and current_row[macd_col] < current_row[signal_col]
    )


class MACDBearishCrossCondition(StrategyCondition):
    """Condition to check for a bearish MACD cross.
    This condition checks if the MACD line crosses below its signal line,
    indicating a potential bearish momentum shift in the market.
    This is typically used in momentum-based strategies to identify potential sell signals.
    This condition is applied to each row of a DataFrame containing MACD and signal line values.
    This condition is useful for strategies that require a bearish momentum shift to enter trades.
    Args:
        macd_col (str): Column name for the MACD values.
        signal_col (str): Column name for the MACD signal line values.

    Returns:
        pd.Series: Boolean Series where True indicates a bearish MACD cross.

    Usage:
        filter = MACDBearishCrossFilter(macd_col='MACD', signal_col='MACD_Signal')
        df['macd_bearish_cross'] = filter.apply(df)
    """

    def __init__(
        self,
        macd_col: SignalStrategyColumns = SignalStrategyColumns.MACD,
        signal_col: SignalStrategyColumns = SignalStrategyColumns.MACD_SIGNAL,
        debug: bool = False,
    ):
        super().__init__(macd_col=macd_col, signal_col=signal_col, debug=debug)
        self.macd_col = macd_col
        self.signal_col = signal_col

    def _apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: macd_bearish_cross(
                row, df.shift(1).loc[row.name], self.macd_col, self.signal_col
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.macd_col, self.signal_col]

    @classmethod
    def available_param_grid(cls) -> dict:
        return {
            "macd_col": [SignalStrategyColumns.MACD],
            "signal_col": [SignalStrategyColumns.MACD_SIGNAL],
        }

    @classmethod
    def optuna_suggest(cls, trial: Trial, prefix: str = ""):
        return cls(
            macd_col=trial.suggest_categorical(
                f"{prefix}macd_col",
                [SignalStrategyColumns.MACD],
            ),
            signal_col=trial.suggest_categorical(
                f"{prefix}signal_col",
                [SignalStrategyColumns.MACD_SIGNAL],
            ),
        )
