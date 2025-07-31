import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedRSIExitCondition(BaseBufferedCondition):
    """
    Buffered RSI Exit Condition
    Triggers when RSI crosses above the overbought threshold.
    """

    def __init__(
        self,
        close_col=SignalStrategyColumns.CLOSE_PRICE,
        period=14,
        overbought=70,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=period + 1)
        self.close_col = close_col
        self.period = period
        self.overbought = overbought

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < self.period + 1:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.period + 1}"
            )
            return False
        df = pd.DataFrame(self.buffer)
        if self.close_col not in df.columns:
            self.logger.error(f"Column {self.close_col} not found in buffer.")
            return False
        close = df[self.close_col]
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.ewm(com=self.period - 1, adjust=False).mean()
        avg_loss = loss.ewm(com=self.period - 1, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))
        latest_rsi = rsi.iloc[-1]
        result = latest_rsi > self.overbought
        self.logger.debug(
            f"Latest RSI: {latest_rsi}, Overbought: {self.overbought}, Result: {result}"
        )
        return result
