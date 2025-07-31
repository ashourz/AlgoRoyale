import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedRSIAboveThresholdCondition(BaseBufferedCondition):
    """
    Buffered RSI Above Threshold Condition
    Triggers when RSI is above a specified threshold.
    """

    def __init__(
        self,
        rsi_col: SignalStrategyColumns = SignalStrategyColumns.RSI,
        threshold=70,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.rsi_col = rsi_col
        self.threshold = threshold

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        if self.rsi_col not in df.columns:
            self.logger.error(f"Column {self.rsi_col} not found in buffer.")
            return False
        value = df[self.rsi_col].iloc[-1] > self.threshold
        self.logger.debug(
            f"RSI: {df[self.rsi_col].iloc[-1]}, Threshold: {self.threshold}, Result: {value}"
        )
        return value
