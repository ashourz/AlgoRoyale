import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedMovingAverageEntryCondition(BaseBufferedCondition):
    """
    Buffered Moving Average Entry Condition
    Triggers when short MA crosses above long MA.
    """

    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        short_window: int = 50,
        long_window: int = 200,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=long_window + 1)
        self.close_col = close_col
        self.short_window = short_window
        self.long_window = long_window

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < self.long_window + 1:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.long_window + 1}"
            )
            return False
        df = pd.DataFrame(self.buffer)
        if self.close_col not in df.columns:
            self.logger.error(f"Column {self.close_col} not found in buffer.")
            return False
        close = df[self.close_col]
        short_ma = close.rolling(window=self.short_window).mean()
        long_ma = close.rolling(window=self.long_window).mean()
        # Crossover: short MA crosses above long MA
        prev = short_ma.iloc[-2] <= long_ma.iloc[-2]
        curr = short_ma.iloc[-1] > long_ma.iloc[-1]
        if prev and curr:
            self.logger.debug(
                f"Short MA crossed above Long MA: {short_ma.iloc[-1]} > {long_ma.iloc[-1]}"
            )
            return True
        return False
