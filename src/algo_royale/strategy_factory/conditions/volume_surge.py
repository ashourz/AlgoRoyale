import pandas as pd

from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.base_strategy_condition import (
    StrategyCondition,
)


@staticmethod
def volume_surge(
    row,
    volume_col: StrategyColumns = StrategyColumns.VOLUME,
    vol_ma_col: StrategyColumns = StrategyColumns.VOL_MA_20,
    threshold=2.0,
):
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

    def __init__(
        self,
        volume_col: StrategyColumns = StrategyColumns.VOLUME,
        vol_ma_col: StrategyColumns = StrategyColumns.VOL_MA_20,
        threshold: float = 2.0,
    ):
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

    @property
    def required_columns(self):
        return [self.volume_col, self.vol_ma_col]

    @classmethod
    def available_param_grid(cls):
        return {
            "volume_col": [StrategyColumns.VOLUME],
            "vol_ma_col": [
                StrategyColumns.VOL_MA_10,
                StrategyColumns.VOL_MA_20,
                StrategyColumns.VOL_MA_50,
                StrategyColumns.VOL_MA_100,
                StrategyColumns.VOL_MA_200,
            ],
            "threshold": [1.2, 1.5, 1.8, 2.0, 2.5, 3.0, 4.0],
        }
