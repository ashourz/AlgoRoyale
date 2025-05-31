import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_filter import StrategyFilter


@staticmethod
def macd_bullish_cross(row, macd_col, signal_col, close_col):
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


class MACDBullishCrossFilter(StrategyFilter):
    """Filter to check if MACD is above its signal line (bullish momentum).
    This filter checks if the MACD line is above its signal line, indicating potential bullish momentum.

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

    def __init__(self, macd_col: str, signal_col: str, close_col: str):
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
