from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.vwap_reversion_entry import (
    VWAPReversionEntryCondition,
)
from algo_royale.strategy_factory.conditions.vwap_reversion_exit import (
    VWAPReversionExitCondition,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class VWAPReversionStrategy(Strategy):
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
                vwap_col=StrategyColumns.VWAP_20,
                vwp_col=StrategyColumns.VOLUME_WEIGHTED_PRICE,
            )
        ],
        exit_conditions: list[VWAPReversionExitCondition] = [
            VWAPReversionExitCondition(
                deviation_threshold=0.01,
                vwap_col=StrategyColumns.VWAP_20,
                vwp_col=StrategyColumns.VOLUME_WEIGHTED_PRICE,
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
