import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def macd_bullish_cross(
    row,
    macd_col: StrategyColumns = StrategyColumns.MACD,
    signal_col: StrategyColumns = StrategyColumns.MACD_SIGNAL,
    close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
) -> bool:
    """
    Returns True if MACD is above its signal line (bullish momentum).
    Assumes you have columns 'macd' and 'macd_signal' in your DataFrame.

    Args:
        row (pd.Series): A row of data.
        macd_col (str): Column name for MACD.
        signal_col (str): Column name for MACD signal line.
        close_col (str): Column name for close price (not used in logic but kept for uniformity).

    Returns:
        bool: True if MACD > signal line, else False.
    """
    return row[macd_col] > row[signal_col]


class MACDBullishCrossCondition(StrategyCondition):
    """Condition to check for a bullish MACD cross.
    This condition checks if the MACD line is above its signal line,
    indicating a potential bullish momentum shift in the market.
    This is typically used in momentum-based strategies to identify potential buy signals.
    This condition is applied to each row of a DataFrame containing MACD and signal line values.
    This condition is useful for strategies that require a bullish momentum shift to enter trades.

    Args:
        macd_col (str): Column name for the MACD values.
        signal_col (str): Column name for the MACD signal line values.
        close_col (str): Column name for the close price (not used in logic but kept for uniformity).

    Returns:
        pd.Series: Boolean Series where True indicates MACD is above the signal line.

    Usage:
        filter = MACDBullishCrossFilter(macd_col='MACD', signal_col='MACD_Signal', close_col='Close')
        df['macd_bullish_cross'] = filter.apply(df)
    """

    def __init__(
        self,
        macd_col: StrategyColumns = StrategyColumns.MACD,
        signal_col: StrategyColumns = StrategyColumns.MACD_SIGNAL,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
    ):
        super().__init__(
            macd_col=macd_col,
            signal_col=signal_col,
            close_col=close_col,
        )
        self.macd_col = macd_col
        self.signal_col = signal_col
        self.close_col = close_col

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: macd_bullish_cross(
                row, self.macd_col, self.signal_col, self.close_col
            ),
            axis=1,
        )

    @property
    def required_columns(self):
        return [self.macd_col, self.signal_col, self.close_col]

    @classmethod
    def available_param_grid(cls):
        return {
            "macd_col": [StrategyColumns.MACD],
            "signal_col": [StrategyColumns.MACD_SIGNAL],
            "close_col": [StrategyColumns.CLOSE_PRICE, StrategyColumns.OPEN_PRICE],
        }
