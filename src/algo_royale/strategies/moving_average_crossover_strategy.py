from typing import List, Optional

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MovingAverageCrossoverStrategy(Strategy):
    """
    Moving Average Crossover Strategy with trend and volume confirmation:
    - Buy when short MA crosses above long MA AND price > trend MA AND volume > volume MA.
    - Sell when short MA crosses below long MA AND price < trend MA AND volume > volume MA.
    - Hold otherwise.

    Parameters:
    - close_col: column name with closing prices.
    - volume_col: column name with volume data.
    - short_window: window size for short moving average.
    - long_window: window size for long moving average.
    - trend_window: window size for trend confirmation moving average.
    - volume_ma_window: window size for volume moving average filter.
    - ma_type: 'ema' or 'sma' (default 'ema').
    """

    def __init__(
        self,
        close_col: str = "close",
        volume_col: Optional[str] = None,
        short_window: int = 10,
        long_window: int = 50,
        trend_window: int = 200,
        volume_ma_window: int = 20,
        ma_type: str = "ema",
    ):
        if (
            short_window <= 0
            or long_window <= 0
            or trend_window <= 0
            or volume_ma_window <= 0
        ):
            raise ValueError("Window sizes must be positive integers.")
        if short_window >= long_window:
            raise ValueError("short_window must be less than long_window.")
        if ma_type not in ("ema", "sma"):
            raise ValueError("ma_type must be either 'ema' or 'sma'.")

        self.close_col = close_col
        self.volume_col = volume_col
        self.short_window = short_window
        self.long_window = long_window
        self.trend_window = trend_window
        self.volume_ma_window = volume_ma_window
        self.ma_type = ma_type

    def _moving_average(self, series: pd.Series, window: int) -> pd.Series:
        if self.ma_type == "ema":
            return series.ewm(span=window, adjust=False).mean()
        else:  # sma
            return series.rolling(window=window, min_periods=window).mean()

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        # Calculate moving averages
        short_ma = self._moving_average(df[self.close_col], self.short_window)
        long_ma = self._moving_average(df[self.close_col], self.long_window)
        trend_ma = self._moving_average(df[self.close_col], self.trend_window)

        # Calculate volume moving average if volume_col is provided
        if self.volume_col and self.volume_col in df.columns:
            vol_ma = (
                df[self.volume_col]
                .rolling(window=self.volume_ma_window, min_periods=1)
                .mean()
            )
            volume_condition = df[self.volume_col] > vol_ma
        else:
            # No volume filtering if volume_col not provided or missing
            volume_condition = pd.Series(True, index=df.index)

        # Base crossover signals
        crossover_signal = pd.Series(0, index=df.index)
        crossover_signal[short_ma > long_ma] = 1
        crossover_signal[short_ma < long_ma] = -1

        signals = pd.Series("hold", index=df.index)

        # Buy signal: crossover bullish + price above trend MA + volume condition
        buy_condition = (
            (crossover_signal == 1)
            & (crossover_signal.shift(1) != 1)
            & (df[self.close_col] > trend_ma)
            & volume_condition
        )

        # Sell signal: crossover bearish + price below trend MA + volume condition
        sell_condition = (
            (crossover_signal == -1)
            & (crossover_signal.shift(1) != -1)
            & (df[self.close_col] < trend_ma)
            & volume_condition
        )

        signals[buy_condition] = "buy"
        signals[sell_condition] = "sell"

        return signals

    def get_required_columns(self) -> List[str]:
        cols = [self.close_col]
        if self.volume_col:
            cols.append(self.volume_col)
        return cols

    def get_min_data_points(self) -> int:
        # Minimum data points to safely calculate all moving averages
        return max(self.trend_window, self.long_window, self.volume_ma_window)
