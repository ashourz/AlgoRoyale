from typing import List

import pandas as pd

from algo_royale.logging.logger_singleton import (
    Environment,
    LoggerSingleton,
    LoggerType,
)
from algo_royale.strategies.base_strategy import Strategy

logger = LoggerSingleton.get_instance(LoggerType.TRADING, Environment.PRODUCTION)


class MovingAverageStrategy(Strategy):
    """
    Enhanced Moving Average Crossover Strategy with:
    - Vectorized signal calculation
    - Additional validation
    - Performance optimizations
    - Configurable signal values
    """

    def __init__(
        self,
        short_window: int = 50,
        long_window: int = 200,
        close_col: str = "close",
        buy_signal: str = "buy",
        sell_signal: str = "sell",
        hold_signal: str = "hold",
    ):
        """
        Args:
            short_window: Short moving average window
            long_window: Long moving average window
            close_col: Name of column containing close prices
            buy_signal: Value to use for buy signals
            sell_signal: Value to use for sell signals
            hold_signal: Value to use for hold signals
        """
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window")

        self.short_window = short_window
        self.long_window = long_window
        self.close_col = close_col
        self.buy_signal = buy_signal
        self.sell_signal = sell_signal
        self.hold_signal = hold_signal

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell/hold signals based on moving average crossover.

        Args:
            df: DataFrame containing price data with at least `close_col`.

        Returns:
            pd.Series: Signals indexed same as input df with values in
                       {buy_signal, sell_signal, hold_signal}.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        if self.close_col not in df.columns:
            raise ValueError(f"DataFrame missing required column: {self.close_col}")

        if len(df) < max(self.short_window, self.long_window):
            logger.info(
                "Not enough data for full windows "
                f"(need at least {max(self.short_window, self.long_window)} rows). "
                "Returning all hold signals."
            )
            return pd.Series(self.hold_signal, index=df.index, name="signal")

        closes = df[self.close_col]

        short_ma = closes.rolling(window=self.short_window, min_periods=1).mean()
        long_ma = closes.rolling(window=self.long_window, min_periods=1).mean()

        # Signal state: 1 if short_ma > long_ma, -1 if short_ma < long_ma, else 0
        signal_state = pd.Series(0, index=df.index)
        signal_state.loc[short_ma > long_ma] = 1
        signal_state.loc[short_ma < long_ma] = -1

        # Initialize all signals as hold
        signals = pd.Series(self.hold_signal, index=df.index, name="signal")

        # Golden Cross (buy): short_ma crosses above long_ma
        golden_cross = (signal_state == 1) & (signal_state.shift(1) != 1)
        signals.loc[golden_cross] = self.buy_signal

        # Death Cross (sell): short_ma crosses below long_ma
        death_cross = (signal_state == -1) & (signal_state.shift(1) != -1)
        signals.loc[death_cross] = self.sell_signal

        # Existing trends - hold buy or sell signals
        signals.loc[(signal_state == 1) & (signals == self.hold_signal)] = (
            self.buy_signal
        )
        signals.loc[(signal_state == -1) & (signals == self.hold_signal)] = (
            self.sell_signal
        )

        return signals

    def get_required_columns(self) -> List[str]:
        """Return list of columns needed in input DataFrame"""
        return [self.close_col]

    def get_min_data_points(self) -> int:
        """Return minimum data points needed to generate signals"""
        return max(self.short_window, self.long_window)
