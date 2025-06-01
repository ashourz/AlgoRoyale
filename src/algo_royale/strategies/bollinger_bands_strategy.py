from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.bollinger_bands_entry import (
    BollingerBandsEntryCondition,
)
from algo_royale.strategies.conditions.bollinger_bands_exit import (
    BollingerBandsExitCondition,
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

    def __init__(
        self,
        window=20,
        num_std=2,
        close_col=StrategyColumns.CLOSE_PRICE,
    ):
        entry_func = BollingerBandsEntryCondition(
            close_col=close_col, window=window, num_std=num_std
        )
        exit_func = BollingerBandsExitCondition(
            close_col=close_col, window=window, num_std=num_std
        )
        super().__init__(entry_conditions=[entry_func], exit_conditions=[exit_func])
