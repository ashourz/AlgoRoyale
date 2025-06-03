from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.moving_average_crossover_entry import (
    MovingAverageCrossoverEntryCondition,
)
from algo_royale.strategy_factory.conditions.moving_average_crossover_exit import (
    MovingAverageCrossoverExitCondition,
)
from algo_royale.strategy_factory.enum.ma_type import MA_Type
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class MovingAverageCrossoverStrategy(Strategy):
    """
    Moving Average Crossover Strategy with trend and volume confirmation.
    This strategy uses a short-term and long-term moving average crossover
    to generate buy and sell signals. It also incorporates a trend filter
    using a longer-term moving average and a volume filter to confirm the strength
    of the signals. The strategy is designed to capture trends in the market
    while filtering out noise and false signals.
    Args:
        close_col (str): Column name for the close price.
        volume_col (Optional[str]): Column name for the volume data. Defaults to None.
        short_window (int): Window size for the short moving average. Defaults to 10.
        long_window (int): Window size for the long moving average. Defaults to 50.
        trend_window (int): Window size for the trend moving average. Defaults to 200.
        volume_ma_window (int): Window size for the volume moving average filter. Defaults to 20.
        ma_type (str): Type of moving average ('ema' or 'sma'). Defaults to 'ema'.
    """

    def __init__(
        self,
        entry_conditions: list[MovingAverageCrossoverEntryCondition] = [
            MovingAverageCrossoverEntryCondition(
                close_col=StrategyColumns.CLOSE_PRICE,
                volume_col=StrategyColumns.VOLUME,
                short_window=10,
                long_window=50,
                trend_window=200,
                volume_ma_window=20,
                ma_type=MA_Type.EMA,
            )
        ],
        exit_conditions: list[MovingAverageCrossoverExitCondition] = [
            MovingAverageCrossoverExitCondition(
                close_col=StrategyColumns.CLOSE_PRICE,
                volume_col=StrategyColumns.VOLUME,
                short_window=10,
                long_window=50,
                trend_window=200,
                volume_ma_window=20,
                ma_type=MA_Type.EMA,
            )
        ],
    ):
        """Initialize the Moving Average Crossover Strategy with entry and exit conditions.
        Parameters:
        - entry_conditions: List of entry conditions for the strategy.
        - exit_conditions: List of exit conditions for the strategy.
        """

        super().__init__(
            entry_conditions=entry_conditions,
            exit_conditions=exit_conditions,
        )
