import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedVolatilityBreakoutEntryCondition(BaseBufferedCondition):
    """
    Buffered Volatility Breakout Entry Condition
    Triggers when price range exceeds a threshold relative to volatility.
    """

    def __init__(
        self,
        threshold=1.5,
        sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
        volatility_col: SignalStrategyColumns = SignalStrategyColumns.VOLATILITY_20,
        range_col: SignalStrategyColumns = SignalStrategyColumns.RANGE,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.threshold = threshold
        self.sma_col = sma_col
        self.volatility_col = volatility_col
        self.range_col = range_col
        self.close_col = close_col

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.sma_col, self.volatility_col, self.range_col, self.close_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        price_range = df[self.range_col].iloc[-1]
        volatility = df[self.volatility_col].iloc[-1]
        result = price_range > (volatility * self.threshold)
        self.logger.debug(
            f"Range: {price_range}, Volatility: {volatility}, Threshold: {self.threshold}, Result: {result}"
        )
        return result
