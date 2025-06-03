from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
from algo_royale.strategy_factory.conditions.volume_surge_exit import (
    VolumeSurgeExitCondition,
)

from .base_strategy import Strategy


class VolumeSurgeStrategy(Strategy):
    """
    Volume Surge Strategy:
    - Buy when current volume exceeds a multiple of the moving average volume.
    - Sell on the next bar after the surge.
    - Hold otherwise.
    """

    def __init__(
        self,
        threshold: float = 2.0,
        ma_window: int = 20,
        vol_col: StrategyColumns = StrategyColumns.VOLUME,
    ):
        self.vol_col = vol_col
        self.threshold = threshold
        self.ma_window = ma_window

        entry_condition = VolumeSurgeEntryCondition(
            vol_col=vol_col, threshold=threshold, ma_window=ma_window
        )
        exit_condition = VolumeSurgeExitCondition(entry_condition=entry_condition)

        self.entry_conditions = [entry_condition]
        self.exit_conditions = [exit_condition]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
