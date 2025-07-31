import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedTimeOfDayEntryCondition(BaseBufferedCondition):
    """
    Buffered Time Of Day Entry Condition
    Triggers when the hour is within the buy window.
    """

    def __init__(
        self,
        buy_start_hour=10,
        buy_end_hour=14,
        hour_col: SignalStrategyColumns = SignalStrategyColumns.HOUR,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.buy_start_hour = buy_start_hour
        self.buy_end_hour = buy_end_hour
        self.hour_col = hour_col
        self.buy_hours = list(range(self.buy_start_hour, self.buy_end_hour + 1))

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        if self.hour_col not in df.columns:
            self.logger.error(f"Column {self.hour_col} not found in buffer.")
            return False
        hour = df[self.hour_col].iloc[-1]
        result = hour in self.buy_hours
        self.logger.debug(
            f"Hour: {hour}, Buy hours: {self.buy_hours}, Result: {result}"
        )
        return result
