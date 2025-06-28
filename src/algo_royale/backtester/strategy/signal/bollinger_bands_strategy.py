from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.bollinger_bands_entry import (
    BollingerBandsEntryCondition,
)
from algo_royale.backtester.strategy.signal.conditions.bollinger_bands_exit import (
    BollingerBandsExitCondition,
)


class BollingerBandsStrategy(BaseSignalStrategy):
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
        entry_conditions: list[BollingerBandsEntryCondition],
        exit_conditions: list[BollingerBandsExitCondition],
    ):
        """Initialize the Bollinger Bands Strategy with entry and exit conditions.
        Parameters:
        - entry_condition: Condition for entering a trade based on Bollinger Bands.
        - exit_condition: Condition for exiting a trade based on Bollinger Bands.
        """
        super().__init__(
            entry_conditions=entry_conditions, exit_conditions=exit_conditions
        )
