from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.moving_average_crossover_entry import (
    MovingAverageCrossoverEntryCondition,
)
from algo_royale.strategies.conditions.moving_average_crossover_exit import (
    MovingAverageCrossoverExitCondition,
)


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
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        volume_col: StrategyColumns = StrategyColumns.VOLUME,
        short_window: int = 10,
        long_window: int = 50,
        trend_window: int = 200,
        volume_ma_window: int = 20,
        ma_type: str = "ema",
    ):
        self.close_col = close_col
        self.volume_col = volume_col
        self.short_window = short_window
        self.long_window = long_window
        self.trend_window = trend_window
        self.volume_ma_window = volume_ma_window
        self.ma_type = ma_type

        self.entry_conditions = [
            MovingAverageCrossoverEntryCondition(
                close_col=close_col,
                volume_col=volume_col,
                short_window=short_window,
                long_window=long_window,
                trend_window=trend_window,
                volume_ma_window=volume_ma_window,
                ma_type=ma_type,
            )
        ]
        self.exit_conditions = [
            MovingAverageCrossoverExitCondition(
                close_col=close_col,
                volume_col=volume_col,
                short_window=short_window,
                long_window=long_window,
                trend_window=trend_window,
                volume_ma_window=volume_ma_window,
                ma_type=ma_type,
            )
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
