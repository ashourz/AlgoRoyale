from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.ema_above_sma_rolling import (
    EMAAboveSMARollingTrend,
)
from algo_royale.strategies.conditions.return_volatility_exit import (
    ReturnVolatilityExit,
)


class TrendScraperStrategy(Strategy):
    """
    Trend Scraper Strategy with flexible trend confirmation and exit conditions.

    Buy when all trend and entry functions return True.
    Sell when any exit function returns True.
    Hold otherwise.
    """

    def __init__(
        self,
        ema_col="ema_20",
        sma_col="sma_20",
        return_col="log_return",
        range_col="range",
        volatility_col="volatility_20",
        window=3,
        threshold=-0.005,
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
        trend_func = EMAAboveSMARollingTrend(
            ema_col=ema_col, sma_col=sma_col, window=window
        )
        exit_func = ReturnVolatilityExit(
            return_col=return_col,
            range_col=range_col,
            volatility_col=volatility_col,
            threshold=threshold,
        )

        super().__init__(trend_funcs=[trend_func], exit_funcs=[exit_func])
