from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedADXBelowThresholdCondition(BaseBufferedCondition):
    def __init__(
        self,
        logger: Loggable,
        adx_col: SignalStrategyColumns = SignalStrategyColumns.ADX,
        threshold: float = 25,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.adx_col = adx_col
        self.threshold = threshold

    def _evaluate_condition(self) -> bool:
        """
        Evaluate the condition based on the current buffer.
        Returns True if the latest ADX value is below the threshold, else False.
        """
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        if len(self.buffer) < self.buffer.maxlen:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.buffer.maxlen}"
            )
            return False

        latest = self.buffer[-1]
        adx_value = latest[self.adx_col]
        result = adx_value < self.threshold
        self.logger.debug(
            f"Buffered ADX: {adx_value}, Threshold: {self.threshold}, Result: {result}"
        )
        return result
