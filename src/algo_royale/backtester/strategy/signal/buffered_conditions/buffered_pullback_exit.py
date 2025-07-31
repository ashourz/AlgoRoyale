from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_pullback_entry import (
    BufferedPullbackEntryCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedPullbackExitCondition(BaseBufferedCondition):
    """
    Buffered Pullback Exit Condition
    Triggers when the buffered entry condition is met, shifted by one bar.
    """

    def __init__(
        self, entry_condition: BufferedPullbackEntryCondition, *, logger: Loggable
    ):
        super().__init__(logger=logger, buffer_size=entry_condition.buffer_size + 1)
        self.entry_condition = entry_condition

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < self.entry_condition.buffer_size + 1:
            self.logger.warning("Buffer not full yet for exit condition.")
            return False
        entry_signal = self.entry_condition._evaluate_condition()
        self.logger.debug(f"Buffered pullback exit uses entry signal: {entry_signal}")
        return entry_signal
