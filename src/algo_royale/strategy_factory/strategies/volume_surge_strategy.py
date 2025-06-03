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
        entry_conditions: list[VolumeSurgeEntryCondition] = [
            VolumeSurgeEntryCondition(
                vol_col=StrategyColumns.VOLUME, threshold=2.0, ma_window=20
            )
        ],
    ):
        """Initialize the Volume Surge Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        """
        self.entry_condition = entry_conditions.first()
        if not self.entry_conditions:
            raise ValueError("At least one entry condition must be provided.")
        self.exit_condition = VolumeSurgeExitCondition(
            entry_condition=self.entry_condition
        )

        self.entry_conditions = [self.entry_condition]
        self.exit_conditions = [self.exit_condition]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
