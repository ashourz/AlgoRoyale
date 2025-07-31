import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedMACDBearishCrossCondition(BaseBufferedCondition):
    """
    Buffered MACD Bearish Cross Condition
    Triggers when MACD crosses below its signal line between previous and current rows.
    """

    def __init__(
        self,
        macd_col: SignalStrategyColumns = SignalStrategyColumns.MACD,
        signal_col: SignalStrategyColumns = SignalStrategyColumns.MACD_SIGNAL,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=2)
        self.macd_col = macd_col
        self.signal_col = signal_col

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < 2:
            self.logger.warning("Buffer not full yet, need at least 2 rows.")
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.macd_col, self.signal_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        prev_row = df.iloc[-2]
        curr_row = df.iloc[-1]
        result = (
            prev_row[self.macd_col] >= prev_row[self.signal_col]
            and curr_row[self.macd_col] < curr_row[self.signal_col]
        )
        self.logger.debug(
            f"Prev MACD: {prev_row[self.macd_col]}, Prev Signal: {prev_row[self.signal_col]}, Curr MACD: {curr_row[self.macd_col]}, Curr Signal: {curr_row[self.signal_col]}, Result: {result}"
        )
        return result
