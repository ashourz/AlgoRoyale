from algo_royale.column_names.strategy_columns import StrategyColumns
from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.rsi_entry import RSIEntryCondition
from algo_royale.strategies.conditions.rsi_exit import RSIExitCondition


class RSIStrategy(Strategy):
    """
    Relative Strength Index (RSI) Strategy

    Generates buy/sell signals based on RSI indicator thresholds.
    Buy when RSI is below oversold threshold, sell when above overbought.
    """

    def __init__(
        self,
        period: int = 14,
        overbought: int = 70,
        oversold: int = 30,
        close_col: str = StrategyColumns.CLOSE_PRICE,
    ) -> None:
        self.close_col = close_col
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

        self.entry_conditions = [
            RSIEntryCondition(close_col=close_col, period=period, oversold=oversold)
        ]
        self.exit_conditions = [
            RSIExitCondition(close_col=close_col, period=period, overbought=overbought)
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            exit_conditions=self.exit_conditions,
        )
