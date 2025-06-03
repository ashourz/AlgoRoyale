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
        window=3,
        threshold=-0.005,
        ema_col=StrategyColumns.EMA_20,
        sma_col=StrategyColumns.SMA_20,
        return_col=StrategyColumns.LOG_RETURN,
        range_col=StrategyColumns.RANGE,
        volatility_col=StrategyColumns.VOLATILITY_20,
    ):
        """
        Parameters:
        - ema_col: Column name for the Exponential Moving Average.
        - sma_col: Column name for the Simple Moving Average.
        - return_col: Column name for the log return.
        - range_col: Column name for the price range.
        - volatility_col: Column name for the volatility measure.
        - window: Rolling window size for trend confirmation.
        - threshold: Threshold for exit condition based on return.
        """
        trend_func = EMAAboveSMARollingCondition(
            ema_col=ema_col, sma_col=sma_col, window=window
        )
        exit_func = ReturnVolatilityExitCondition(
            return_col=return_col,
            range_col=range_col,
            volatility_col=volatility_col,
            threshold=threshold,
        )

        super().__init__(trend_conditions=[trend_func], exit_conditions=[exit_func])
