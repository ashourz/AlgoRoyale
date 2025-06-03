from algo_royale.strategy_factory.conditions.combo_entry import ComboEntryCondition
from algo_royale.strategy_factory.conditions.combo_exit import ComboExitCondition
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class ComboStrategy(Strategy):
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
    ):
        super().__init__(
            entry_conditions=entry_conditions, exit_conditions=exit_conditions
        )
