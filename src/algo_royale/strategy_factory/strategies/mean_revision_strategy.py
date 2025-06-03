from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategy_factory.conditions.price_above_sma import (
    PriceAboveSMACondition,
)
from algo_royale.strategy_factory.stateful_logic.mean_reversion_stategul_logic import (
    MeanReversionStatefulLogic,
)
from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class MeanReversionStrategy(Strategy):
    """
    Mean Reversion Strategy with trailing stop, profit target, trend filter, and re-entry cooldown.
    This strategy identifies mean reversion opportunities based on the deviation of the price
    from a Simple Moving Average (SMA). It enters trades when the price deviates significantly
    from the SMA and exits based on a trailing stop, profit target, or reversion to the mean.
    The strategy uses a trend condition to filter trades, ensuring that trades are only taken
    when the price is above a specified SMA, indicating a bullish trend.
    Args:
        close_col (str): Column name for the close price.
        sma_col (str): Column name for the SMA values.
        window (int): Window size for the SMA.
        threshold (float): Deviation threshold to trigger buy/sell signals.
        stop_pct (float): Percentage for trailing stop loss.
        profit_target_pct (float): Percentage for profit target.
        reentry_cooldown (int): Number of periods to wait before re-entering after an exit.
    """

    def __init__(
        self,
        window: int = 20,
        threshold: float = 0.02,
        stop_pct: float = 0.02,
        profit_target_pct: float = 0.04,
        reentry_cooldown: int = 5,
        close_col: StrategyColumns = StrategyColumns.CLOSE_PRICE,
        sma_col: StrategyColumns = StrategyColumns.SMA_200,
    ):
        self.close_col = close_col
        self.window = window
        self.threshold = threshold
        self.stop_pct = stop_pct
        self.profit_target_pct = profit_target_pct
        self.trend_condition = [
            PriceAboveSMACondition(price_col=close_col, sma_col=sma_col)
        ]
        self.stateful_logic = MeanReversionStatefulLogic(
            window=window,
            threshold=threshold,
            stop_pct=stop_pct,
            profit_target_pct=profit_target_pct,
            reentry_cooldown=reentry_cooldown,
            close_col=close_col,
        )
        self.reentry_cooldown = reentry_cooldown

        super().__init__(
            trend_conditions=self.trend_conditions, stateful_logic=self.stateful_logic
        )
