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
        buffer_size: int = 1,  # For ADX, 1 is usually enough, but you can increase if needed
    ):
        super().__init__(logger=logger, buffer_size=buffer_size)
        self.threshold = threshold
        self.adx_col = adx_col

    def update(self, adx_value: float) -> bool:
        self.adx_values.append(adx_value)
        if len(self.adx_values) > self.window:
            self.adx_values.pop(0)
        return len(self.adx_values) == self.window and all(
            adx < self.threshold for adx in self.adx_values
        )

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
