from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.conditions.volume_surge_entry import (
    VolumeSurgeEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.volume_surge_exit import (
    VolumeSurgeExitCondition,
)
from algo_royale.logging.loggable import Loggable
from src.algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)


class VolumeSurgeStrategy(BaseSignalStrategy):
    """
    Volume Surge Strategy:
    - Buy when current volume exceeds a multiple of the moving average volume.
    - Sell on the next bar after the surge.
    - Hold otherwise.
    """

    def __init__(
        self,
        logger: Loggable,
        entry_conditions: list[VolumeSurgeEntryCondition] = [
            VolumeSurgeEntryCondition(
                vol_col=SignalStrategyColumns.VOLUME, threshold=2.0, ma_window=20
            )
        ],
    ):
        """Initialize the Volume Surge Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        """
        self.entry_conditions = entry_conditions
        if not self.entry_conditions:
            raise ValueError("At least one entry condition must be provided.")
        self.entry_condition = self.entry_conditions[0]
        self.exit_condition = VolumeSurgeExitCondition(
            entry_condition=self.entry_condition
        )

        self.exit_conditions = [self.exit_condition]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
            logger=logger,
        )
