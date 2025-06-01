import pandas as pd

from algo_royale.strategies.strategy_filters.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def volume_surge(row, volume_col, vol_ma_col, threshold=2.0):
    """
    Returns True if the current volume is greater than a multiple of its moving average,
    indicating a volume surge.

    Args:
        row (pd.Series): A row of data.
        volume_col (str): Column name for volume.
        vol_ma_col (str): Column name for volume moving average.
        threshold (float, optional): Multiplier threshold. Default is 2.0.

    Returns:
        bool: True if volume surges above threshold * moving average, else False.
    """
    return row[volume_col] > threshold * row[vol_ma_col]


class VolumeSurgeCondition(StrategyCondition):
    """Condition to check for a volume surge.
    This condition checks if the current volume is greater than a specified multiple of its moving average,
    indicating a significant increase in trading activity. This is typically used to identify potential
    breakouts or significant market movements.

    Args:
        volume_col (str): Column name for volume.
        vol_ma_col (str): Column name for volume moving average.
        threshold (float, optional): Multiplier threshold. Default is 2.0.

    Returns:
        pd.Series: Boolean Series where True indicates a volume surge.

    Usage:
        filter = VolumeSurgeFilter(volume_col='Volume', vol_ma_col='Volume_MA', threshold=2.0)
        df['volume_surge'] = filter.apply(df)
    """

    def __init__(self, volume_col: str, vol_ma_col: str, threshold: float = 2.0):
        self.volume_col = volume_col
        self.vol_ma_col = vol_ma_col
        self.threshold = threshold

    def apply(self, df: pd.DataFrame) -> pd.Series:
        return df.apply(
            lambda row: volume_surge(
                row, self.volume_col, self.vol_ma_col, self.threshold
            ),
            axis=1,
        )
