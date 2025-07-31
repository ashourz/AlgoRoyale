import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.strategy.signal.buffered_conditions.buffered_condition import (
    BaseBufferedCondition,
)
from algo_royale.logging.loggable import Loggable


class BufferedBollingerBandsEntry(BaseBufferedCondition):
    """
    Buffered Bollinger Bands Entry Condition
    This condition checks if the price is below the lower Bollinger Band.
    """

    def __init__(
        self,
        logger: Loggable,
        close_col: SignalStrategyColumns = SignalStrategyColumns.CLOSE_PRICE,
        window=20,
        num_std=2,
    ):
        super().__init__(logger=logger, buffer_size=window)
        self.close_col = close_col
        self.window = window
        self.num_std = num_std

    def _evaluate_condition(self) -> bool:
        """
        Evaluate the condition based on the current buffer.
        Returns True if the latest price is below the lower Bollinger Band, else False.
        """
        if not self.buffer:
            self.logger.warning("Buffer is empty, cannot evaluate condition.")
            return False
        if len(self.buffer) < self.window:
            self.logger.warning(
                f"Buffer not full yet, current size: {len(self.buffer)}, required: {self.window}"
            )
            return False

        df = pd.DataFrame(self.buffer)
        rolling_mean = df[self.close_col].rolling(window=self.window).mean()
        rolling_std = df[self.close_col].rolling(window=self.window).std()
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        valid_idx = rolling_mean.notna()
        if not valid_idx.iloc[-1]:
            self.logger.warning(
                "Latest rolling mean is NaN, cannot evaluate condition."
            )
            return False
        # Check the latest price against the lower band
        if self.close_col not in df.columns:
            self.logger.error(f"Column {self.close_col} not found in buffer.")
            return False
        if lower_band.isna().all():
            self.logger.error("Lower band is NaN, cannot evaluate condition.")
            return False
        if upper_band.isna().all():
            self.logger.error("Upper band is NaN, cannot evaluate condition.")
            return False
        # Get the latest price
        latest_price = df[self.close_col].iloc[-1]
        result = (latest_price < lower_band.iloc[-1]) or (
            latest_price > upper_band.iloc[-1]
        )
        self.logger.debug(
            f"Latest Price: {latest_price}, Lower Band: {lower_band.iloc[-1]}, Upper Band: {upper_band.iloc[-1]}, Result: {result}"
        )
        return result
