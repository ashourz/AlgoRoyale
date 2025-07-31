import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedPullbackEntryCondition(BaseBufferedCondition):
    """
    Buffered Pullback Entry Condition
    Triggers when price crosses above MA after being below.
    """

    def __init__(
        self,
        ma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_20,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=2)
        self.ma_col = ma_col
        self.close_col = close_col

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < 2:
            self.logger.warning("Buffer not full yet, need at least 2 rows.")
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.ma_col, self.close_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        above_ma = df[self.close_col].iloc[-1] > df[self.ma_col].iloc[-1]
        below_ma_yesterday = df[self.close_col].iloc[-2] < df[self.ma_col].iloc[-2]
        result = above_ma and below_ma_yesterday
        self.logger.debug(
            f"Pullback: above_ma={above_ma}, below_ma_yesterday={below_ma_yesterday}, Result: {result}"
        )
        return result
