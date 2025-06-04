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
        trend_conditions: list[MeanReversionStatefulLogic] = [
            PriceAboveSMACondition(
                close_col=StrategyColumns.CLOSE_PRICE, sma_col=StrategyColumns.SMA_200
            )
        ],
        stateful_logic: MeanReversionStatefulLogic = MeanReversionStatefulLogic(
            window=20,
            threshold=0.02,
            stop_pct=0.02,
            profit_target_pct=0.04,
            reentry_cooldown=5,
            close_col=StrategyColumns.CLOSE_PRICE,
        ),
    ):
        """Initialize the Mean Reversion Strategy with trend conditions and stateful logic.
        Parameters:
        - trend_conditions: List of trend conditions to filter trades.
        - stateful_logic: Stateful logic for managing trades and positions.
        """
        super().__init__(
            trend_conditions=trend_conditions, stateful_logic=stateful_logic
        )
