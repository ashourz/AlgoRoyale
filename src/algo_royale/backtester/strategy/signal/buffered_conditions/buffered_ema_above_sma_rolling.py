import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedEMAAboveSMARollingCondition(BaseBufferedCondition):
    """
    Buffered EMA Above SMA Rolling Condition
    Triggers when EMA is above SMA and rising for a rolling window.
    """

    def __init__(
        self,
        ema_col: SignalStrategyColumns = SignalStrategyColumns.EMA_20,
        sma_col: SignalStrategyColumns = SignalStrategyColumns.SMA_50,
        window: int = 3,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=window)
        self.ema_col = ema_col
        self.sma_col = sma_col
        self.window = window

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < self.window:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.window}"
            )
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.ema_col, self.sma_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        trend = (df[self.ema_col] > df[self.sma_col]) & (
            df[self.ema_col] > df[self.ema_col].shift(1)
        )
        result = trend.iloc[-self.window :].sum() == self.window
        self.logger.debug(
            f"EMA: {df[self.ema_col].iloc[-1]}, SMA: {df[self.sma_col].iloc[-1]}, Window: {self.window}, Result: {result}"
        )
        return result
