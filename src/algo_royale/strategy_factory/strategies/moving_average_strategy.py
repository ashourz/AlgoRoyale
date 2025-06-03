from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.moving_average_entry import (
    MovingAverageEntryCondition,
)
from algo_royale.strategy_factory.conditions.moving_average_exit import (
    MovingAverageExitCondition,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class MovingAverageStrategy(Strategy):
    """
    Enhanced Moving Average Crossover Strategy using modular entry/exit conditions.
    This strategy uses short-term and long-term moving averages to generate buy and sell signals.
    It incorporates entry and exit conditions based on moving average crossovers.
    Parameters:
    - short_window: Window size for the short moving average (default is 50).
    - long_window: Window size for the long moving average (default is 200).
    - close_col: Column name for the close price (default is "close").
    - buy_signal: Signal name for buy actions (default is "buy").
    - sell_signal: Signal name for sell actions (default is "sell").
    - hold_signal: Signal name for hold actions (default is "hold").
    """

    def __init__(
        self,
        short_window: int = 50,
        long_window: int = 200,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        buy_signal: str = "buy",
        sell_signal: str = "sell",
        hold_signal: str = "hold",
    ):
        self.short_window = short_window
        self.long_window = long_window
        self.close_col = close_col
        self.buy_signal = buy_signal
        self.sell_signal = sell_signal
        self.hold_signal = hold_signal

        self.entry_conditions = [
            MovingAverageEntryCondition(
                close_col=close_col,
                short_window=short_window,
                long_window=long_window,
            )
        ]
        self.exit_conditions = [
            MovingAverageExitCondition(
                close_col=close_col,
                short_window=short_window,
                long_window=long_window,
            )
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
