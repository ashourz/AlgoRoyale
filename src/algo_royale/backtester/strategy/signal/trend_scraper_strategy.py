from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)
from algo_royale.backtester.strategy.signal.conditions.ema_above_sma_rolling import (
    EMAAboveSMARollingCondition,
)
from algo_royale.backtester.strategy.signal.conditions.return_volatility_exit import (
    ReturnVolatilityExitCondition,
)
from algo_royale.logging.loggable import Loggable


class TrendScraperStrategy(BaseSignalStrategy):
    """
    Trend Scraper Strategy with flexible trend confirmation and exit conditions.

    Buy when all trend and entry functions return True.
    Sell when any exit function returns True.
    Hold otherwise.
    """

    def __init__(
        self,
        logger: Loggable,
        trend_conditions: list[EMAAboveSMARollingCondition] = [
            EMAAboveSMARollingCondition(
                ema_col=SignalStrategyColumns.EMA_20,
                sma_col=SignalStrategyColumns.SMA_50,
                window=3,
            )
        ],
        exit_conditions: list[ReturnVolatilityExitCondition] = [
            ReturnVolatilityExitCondition(
                return_col=SignalStrategyColumns.LOG_RETURN,
                range_col=SignalStrategyColumns.RANGE,
                volatility_col=SignalStrategyColumns.VOLATILITY_20,
                threshold=-0.005,
            )
        ],
    ):
        """Initialize the Trend Scraper Strategy with trend and exit conditions.
        Parameters:
        - trend_conditions: List of trend conditions for the strategy.
        - exit_conditions: List of exit conditions for the strategy.
        """
        super().__init__(
            trend_conditions=trend_conditions,
            exit_conditions=exit_conditions,
            logger=logger,
        )
