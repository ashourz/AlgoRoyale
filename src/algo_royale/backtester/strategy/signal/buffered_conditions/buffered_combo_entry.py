import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedComboEntryCondition(BaseBufferedCondition):
    """
    Buffered Combo Entry Condition
    Triggers when RSI < rsi_buy_thresh, MACD > macd_buy_thresh, and Volume > vol_ma.
    """

    def __init__(
        self,
        rsi_buy_thresh,
        macd_buy_thresh,
        rsi_col: SignalStrategyColumns = SignalStrategyColumns.RSI,
        macd_col: SignalStrategyColumns = SignalStrategyColumns.MACD,
        volume_col: SignalStrategyColumns = SignalStrategyColumns.VOLUME,
        vol_ma_col: SignalStrategyColumns = SignalStrategyColumns.VOL_MA_20,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=1)
        self.rsi_col = rsi_col
        self.macd_col = macd_col
        self.volume_col = volume_col
        self.vol_ma_col = vol_ma_col
        self.rsi_buy_thresh = rsi_buy_thresh
        self.macd_buy_thresh = macd_buy_thresh

    def _evaluate_condition(self) -> bool:
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        df = pd.DataFrame(self.buffer)
        for col in [self.rsi_col, self.macd_col, self.volume_col, self.vol_ma_col]:
            if col not in df.columns:
                self.logger.error(f"Column {col} not found in buffer.")
                return False
        row = df.iloc[-1]
        result = (
            (row[self.rsi_col] < self.rsi_buy_thresh)
            and (row[self.macd_col] > self.macd_buy_thresh)
            and (row[self.volume_col] > row[self.vol_ma_col])
        )
        self.logger.debug(
            f"Combo: RSI {row[self.rsi_col]}, MACD {row[self.macd_col]}, Volume {row[self.volume_col]}, VolMA {row[self.vol_ma_col]}, Result: {result}"
        )
        return result
