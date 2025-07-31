import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedBooleanColumnEntryCondition(BaseBufferedCondition):
    """
    Buffered Boolean Column Entry Condition
    Triggers when the specified boolean column is True in the latest buffer row.
    """

    def __init__(
        self,
        entry_col: SignalStrategyColumns = SignalStrategyColumns.ENTRY_SIGNAL,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.entry_col = entry_col

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        if self.entry_col not in df.columns:
            self.logger.error(f"Column {self.entry_col} not found in buffer.")
            return False
        value = bool(df[self.entry_col].iloc[-1])
        self.logger.debug(f"Boolean column {self.entry_col} value: {value}")
        return value
