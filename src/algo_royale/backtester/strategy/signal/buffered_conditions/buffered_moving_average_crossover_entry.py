import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enum.ma_type import MA_Type
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedMovingAverageCrossoverEntryCondition(BaseBufferedCondition):
    """
    Buffered Moving Average Crossover Entry Condition
    Triggers when short MA crosses above long MA, with trend and volume filters.
    """

    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        volume_col: SignalStrategyColumns = SignalStrategyColumns.VOLUME,
        short_window: int = 10,
        long_window: int = 50,
        trend_window: int = 200,
        volume_ma_window: int = 20,
        ma_type: MA_Type = MA_Type.EMA,
        *,
        logger: Loggable,
    ):
        super().__init__(
            logger=logger,
            buffer_size=max(long_window, trend_window, volume_ma_window) + 1,
        )
        self.close_col = close_col
        self.volume_col = volume_col
        self.short_window = short_window
        self.long_window = long_window
        self.trend_window = trend_window
        self.volume_ma_window = volume_ma_window
        self.ma_type = ma_type

    def _ma(self, series, window):
        if self.ma_type == MA_Type.EMA:
            return series.ewm(span=window, adjust=False).mean()
        else:
            return series.rolling(window=window).mean()

    def _evaluate_condition(self) -> bool:
        if (
            not self.buffer
            or len(self.buffer)
            < max(self.long_window, self.trend_window, self.volume_ma_window) + 1
        ):
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {max(self.long_window, self.trend_window, self.volume_ma_window) + 1}"
            )
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.close_col, self.volume_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        close = df[self.close_col]
        volume = df[self.volume_col]
        short_ma = self._ma(close, self.short_window)
        long_ma = self._ma(close, self.long_window)
        trend_ma = self._ma(close, self.trend_window)
        volume_ma = self._ma(volume, self.volume_ma_window)
        prev_cross = short_ma.iloc[-2] <= long_ma.iloc[-2]
        curr_cross = short_ma.iloc[-1] > long_ma.iloc[-1]
        price_above_trend = close.iloc[-1] > trend_ma.iloc[-1]
        volume_above_ma = volume.iloc[-1] > volume_ma.iloc[-1]
        if prev_cross and curr_cross and price_above_trend and volume_above_ma:
            self.logger.debug("MA crossover with trend/volume filter triggered.")
            return True
        return False
