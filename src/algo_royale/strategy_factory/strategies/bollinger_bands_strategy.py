from algo_royale.strategy_factory.conditions.bollinger_bands_entry import (
    BollingerBandsEntryCondition,
)
from algo_royale.strategy_factory.conditions.bollinger_bands_exit import (
    BollingerBandsExitCondition,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands Strategy using the modular function approach.
    Buy when price falls below the lower band,
    sell when price rises above the upper band,
    otherwise hold.
    This strategy uses Bollinger Bands to determine entry and exit points.
    It combines entry and exit conditions based on the Bollinger Bands indicators.
    Parameters:
    - entry_condition: Condition for entering a trade based on Bollinger Bands.
    - exit_condition: Condition for exiting a trade based on Bollinger Bands.
    """

    def __init__(
        self,
        entry_condition: BollingerBandsEntryCondition,
        exit_condition: BollingerBandsExitCondition,
    ):
        """Initialize the Bollinger Bands Strategy with entry and exit conditions.
        Parameters:
        - entry_condition: Condition for entering a trade based on Bollinger Bands.
        - exit_condition: Condition for exiting a trade based on Bollinger Bands.
        """
        super().__init__(
            entry_conditions=[entry_condition], exit_conditions=[exit_condition]
        )

    @classmethod
    def all_strategy_combinations(cls):
        entry_variants = BollingerBandsEntryCondition.all_possible_conditions()
        exit_variants = BollingerBandsExitCondition.all_possible_conditions()
        strategies = []
        for entry in entry_variants:
            for exit in exit_variants:
                strategies.append(cls(entry_condition=entry, exit_condition=exit))
        return strategies
