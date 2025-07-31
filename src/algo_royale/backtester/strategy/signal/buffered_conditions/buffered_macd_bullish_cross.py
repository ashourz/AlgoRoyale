import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedMACDBullishCrossCondition(BaseBufferedCondition):
    """
    Buffered MACD Bullish Cross Condition
    Triggers when MACD is above its signal line.
    """

    def __init__(
        self,
        macd_col: SignalStrategyColumns = SignalStrategyColumns.MACD,
        signal_col: SignalStrategyColumns = SignalStrategyColumns.MACD_SIGNAL,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.macd_col = macd_col
        self.signal_col = signal_col

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.macd_col, self.signal_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        result = df[self.macd_col].iloc[-1] > df[self.signal_col].iloc[-1]
        self.logger.debug(
            f"MACD: {df[self.macd_col].iloc[-1]}, Signal: {df[self.signal_col].iloc[-1]}, Result: {result}"
        )
        return result
