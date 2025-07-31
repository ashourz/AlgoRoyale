import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedVolumeSurgeEntryCondition(BaseBufferedCondition):
    """
    Buffered Volume Surge Entry Condition
    Triggers when volume exceeds moving average by a threshold.
    """

    def __init__(
        self,
        vol_col=SignalStrategyColumns.VOLUME,
        threshold=2.0,
        ma_window=20,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=ma_window)
        self.vol_col = vol_col
        self.threshold = threshold
        self.ma_window = ma_window

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < self.ma_window:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.ma_window}"
            )
            return False
        df = pd.DataFrame(self.buffer)
        if self.vol_col not in df.columns:
            self.logger.error(f"Column {self.vol_col} not found in buffer.")
            return False
        vol_ma = (
            df[self.vol_col]
            .rolling(window=self.ma_window, min_periods=1)
            .mean()
            .iloc[-1]
        )
        surge = df[self.vol_col].iloc[-1] > (vol_ma * self.threshold)
        self.logger.debug(
            f"Volume: {df[self.vol_col].iloc[-1]}, MA: {vol_ma}, Threshold: {self.threshold}, Result: {surge}"
        )
        return surge
