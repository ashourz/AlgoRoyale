import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedMomentumEntryCondition(BaseBufferedCondition):
    """
    Buffered Momentum Entry Condition
    Triggers when momentum exceeds a threshold, with optional smoothing and confirmation.
    """

    def __init__(
        self,
        close_col=SignalStrategyColumns.CLOSE_PRICE,
        lookback=10,
        threshold=0.0,
        smooth_window=None,
        confirmation_periods=1,
        *,
        logger: Loggable,
    ):
        buffer_size = (
            (lookback if lookback else 1)
            + (smooth_window if smooth_window else 0)
            + (confirmation_periods if confirmation_periods else 1)
        )
        super().__init__(logger=logger, buffer_size=buffer_size)
        self.close_col = close_col
        self.lookback = lookback
        self.threshold = threshold
        self.smooth_window = smooth_window
        self.confirmation_periods = confirmation_periods

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < self.buffer_size:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.buffer_size}"
            )
            return False
        df = pd.DataFrame(self.buffer)
        if self.close_col not in df.columns:
            self.logger.error(f"Column {self.close_col} not found in buffer.")
            return False
        momentum = df[self.close_col].pct_change(periods=self.lookback)
        if self.smooth_window:
            momentum = momentum.rolling(window=self.smooth_window).mean()
        if self.confirmation_periods > 1:
            recent = momentum.iloc[-self.confirmation_periods :]
            result = (recent > self.threshold).all()
        else:
            result = momentum.iloc[-1] > self.threshold
        self.logger.debug(
            f"Momentum: {momentum.iloc[-1]}, Threshold: {self.threshold}, Result: {result}"
        )
        return result
