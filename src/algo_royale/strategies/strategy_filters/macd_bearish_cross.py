import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def macd_bearish_cross(current_row, prev_row, macd_col, signal_col):
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


class MACDBearishCrossFilter(StrategyFilter):
    """Filter to check for a bearish MACD cross.
    This filter checks if the MACD line crosses below its signal line, indicating potential bearish momentum.

    Args:
        macd_col (str): Column name for the MACD values.
        signal_col (str): Column name for the MACD signal line values.

    Returns:
        pd.Series: Boolean Series where True indicates a bearish MACD cross.

    Usage:
        filter = MACDBearishCrossFilter(macd_col='MACD', signal_col='MACD_Signal')
        df['macd_bearish_cross'] = filter.apply(df)
    """

    def __init__(self, macd_col: str, signal_col: str):
        self.macd_col = macd_col
        self.signal_col = signal_col

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: macd_bearish_cross(
                row, df.shift(1).loc[row.name], self.macd_col, self.signal_col
            ),
            axis=1,
        )
