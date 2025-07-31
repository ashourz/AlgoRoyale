import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedBollingerBandsExitCondition(BaseBufferedCondition):
    """
    Buffered Bollinger Bands Exit Condition
    Triggers when price is above the upper band.
    """

    def __init__(
        self,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        window=20,
        num_std=2,
        *,
        logger: Loggable,
    ):
        super().__init__(logger=logger, buffer_size=window)
        self.close_col = close_col
        self.window = window
        self.num_std = num_std

    def _evaluate_condition(self) -> bool:
        if not self.buffer or len(self.buffer) < self.window:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.window}"
            )
            return False
        df = pd.DataFrame(self.buffer)
        if self.close_col not in df.columns:
            self.logger.error(f"Column {self.close_col} not found in buffer.")
            return False
        close = df[self.close_col]
        rolling_mean = close.rolling(window=self.window).mean()
        rolling_std = close.rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        price = close.iloc[-1]
        valid = not pd.isna(rolling_mean.iloc[-1])
        result = valid and price > upper_band.iloc[-1]
        self.logger.debug(
            f"Price: {price}, Upper Band: {upper_band.iloc[-1]}, Result: {result}"
        )
        return result
