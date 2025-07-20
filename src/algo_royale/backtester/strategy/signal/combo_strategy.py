from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.combo_entry import (
    ComboEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.combo_exit import (
    ComboExitCondition,
)


class ComboStrategy(BaseSignalStrategy):
    """
    Combo Strategy using RSI, MACD, and volume conditions for trading decisions.
    Buy when all entry conditions are met.
    Sell when any exit condition is met.
    Hold otherwise.
    This strategy combines multiple entry and exit conditions into a single strategy.
    Parameters:
    - entry_condition: Condition for entering a trade based on a combination of indicators.
    - exit_condition: Condition for exiting a trade based on a combination of indicators.
    """

    def __init__(
        self,
        entry_conditions: list[ComboEntryCondition],
        exit_conditions: list[ComboExitCondition],
        debug: bool = False,
    ):
        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
            debug=debug,
        )
