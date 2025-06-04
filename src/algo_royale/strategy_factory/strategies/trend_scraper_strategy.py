from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.ema_above_sma_rolling import (
    EMAAboveSMARollingCondition,
)
from algo_royale.strategy_factory.conditions.return_volatility_exit import (
    ReturnVolatilityExitCondition,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class TrendScraperStrategy(Strategy):
    """
    Trend Scraper Strategy with flexible trend confirmation and exit conditions.

    Buy when all trend and entry functions return True.
    Sell when any exit function returns True.
    Hold otherwise.
    """

    def __init__(
        self,
        trend_conditions: list[EMAAboveSMARollingCondition] = [
            EMAAboveSMARollingCondition(
                ema_sma_pair=(StrategyColumns.EMA_20, StrategyColumns.SMA_50),
                window=3,
            )
        ],
        exit_conditions: list[ReturnVolatilityExitCondition] = [
            ReturnVolatilityExitCondition(
                return_col=StrategyColumns.LOG_RETURN,
                range_col=StrategyColumns.RANGE,
                volatility_col=StrategyColumns.VOLATILITY_20,
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
            trend_conditions=trend_conditions, exit_conditions=exit_conditions
        )
