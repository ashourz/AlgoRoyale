from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.vwap_reversion_entry import (
    VWAPReversionEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.vwap_reversion_exit import (
    VWAPReversionExitCondition,
)


class VWAPReversionStrategy(BaseSignalStrategy):
    """
    VWAP Reversion Strategy:
    - Buy when volume-weighted price is significantly below the VWAP.
    - Sell when volume-weighted price is significantly above the VWAP.
    - Hold otherwise.
    """

    def __init__(
        self,
        entry_conditions: list[VWAPReversionEntryCondition] = [
            VWAPReversionEntryCondition(
                deviation_threshold=0.01,
                vwap_col=SignalStrategyColumns.VWAP_20,
                vwp_col=SignalStrategyColumns.VOLUME_WEIGHTED_PRICE,
            )
        ],
        exit_conditions: list[VWAPReversionExitCondition] = [
            VWAPReversionExitCondition(
                deviation_threshold=0.01,
                vwap_col=SignalStrategyColumns.VWAP_20,
                vwp_col=SignalStrategyColumns.VOLUME_WEIGHTED_PRICE,
            )
        ],
    ):
        """Initialize the VWAP Reversion Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        - exit_conditions: List of exit conditions for the strategy.
        """

        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
        )
