from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.bollinger_bands_entry import (
    BollingerBandsEntry,
)
from algo_royale.strategies.conditions.bollinger_bands_exit import (
    BollingerBandsExit,
)


class BollingerBandsStrategy(Strategy):
    """
    Bollinger Bands Strategy using the modular function approach.
    Buy when price falls below the lower band,
    sell when price rises above the upper band,
    otherwise hold.
    Parameters:
    - close_col: Column name for the closing prices.
    - window: Rolling window size for calculating the Bollinger Bands (default is 20).
    - num_std: Number of standard deviations for the bands (default is 2).
    """

    def __init__(self, close_col="close", window=20, num_std=2):
        entry_func = BollingerBandsEntry(
            close_col=close_col, window=window, num_std=num_std
        )
        exit_func = BollingerBandsExit(
            close_col=close_col, window=window, num_std=num_std
        )
        super().__init__(entry_conditions=[entry_func], exit_conditions=[exit_func])
