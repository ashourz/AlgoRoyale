from collections import deque

from algo_royale.logging.loggable import Loggable


class BaseBufferedCondition:
    """
    Buffered version of ADXAboveThresholdCondition for live data.
    Maintains a buffer and checks if the latest ADX value is above the threshold.
    """

    def __init__(
        self,
        logger: Loggable,
        buffer_size: int = 1,
    ):
        self.buffer = deque(maxlen=buffer_size)
        self.logger = logger

    def update(self, row: dict) -> bool:
        """
        Update the buffer with a new row (dict or pd.Series) and check the condition.
        Returns True if the condition is met, else False.
        """
        self._update_buffer(row)
        return self._evaluate_condition()

    def _update_buffer(self, row: dict):
        """
        Update the buffer with a new row (dict or pd.Series) and check the condition.
        Returns True if ADX > threshold, else False.
        """
        self.buffer.append(row)
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        if len(self.buffer) < self.buffer.maxlen:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.buffer.maxlen}"
            )
            return False
        if len(self.buffer) > self.buffer.maxlen:
            self.logger.warning(
                f"Buffer exceeded max size, current size: {len(self.buffer)}, max size: {self.buffer.maxlen}"
            )
            self.buffer.pop()  # Maintain buffer size

    def _evaluate_condition(self) -> bool:
        """
        Evaluate the condition based on the current buffer.
        Subclasses should implement this method to define the specific condition logic.
        """
        raise NotImplementedError("Subclasses must implement evaluate_condition()")
