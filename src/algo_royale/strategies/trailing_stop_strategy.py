from typing import Callable, Optional

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class TrailingStopStrategy(Strategy):
    def __init__(
        self,
        close_col: str = "close_price",
        stop_pct: float = 0.02,
        entry_condition_col: Optional[str] = None,
        trend_filter_col: Optional[str] = None,
        trend_filter_func: Optional[Callable[[pd.Series, str, str], bool]] = None,
    ):
        """
        Parameters:
        - close_col: column name for price data
        - stop_pct: trailing stop percentage (0 < stop_pct < 1)
        - entry_condition_col: optional boolean column for entry signals
        - trend_filter_col: optional column used for trend confirmation (e.g., SMA)
        - trend_filter_func: function(row, trend_filter_col, close_col) -> bool
          Returns True if trend is confirmed, else False.
        """
        if not (0 < stop_pct < 1):
            raise ValueError("stop_pct must be between 0 and 1")

        self.close_col = close_col
        self.stop_pct = stop_pct
        self.entry_condition_col = entry_condition_col
        self.trend_filter_col = trend_filter_col
        self.trend_filter_func = trend_filter_func

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy/hold/sell signals based on trailing stop logic.

        Buy when entry condition and trend filter (if any) are satisfied.
        Update trailing stop as price moves up.
        Sell when price falls below trailing stop.
        """
        required_cols = {self.close_col}
        if self.entry_condition_col is not None:
            required_cols.add(self.entry_condition_col)
        if self.trend_filter_col is not None:
            required_cols.add(self.trend_filter_col)

        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

        signals = pd.Series("hold", index=df.index, name="signal")
        in_position = False
        trailing_stop = None

        for i in range(len(df)):
            row = df.iloc[i]
            price = row[self.close_col]

            # Entry condition
            entry_signal = self.entry_condition_col is None or bool(
                row[self.entry_condition_col]
            )

            # Trend filter condition
            trend_ok = True
            if self.trend_filter_col and self.trend_filter_func:
                trend_ok = self.trend_filter_func(
                    row, self.trend_filter_col, self.close_col
                )

            if not in_position:
                if entry_signal and trend_ok:
                    signals.iat[i] = "buy"
                    in_position = True
                    trailing_stop = price * (1 - self.stop_pct)
            else:
                # Update trailing stop if price moves up sufficiently
                new_stop = price * (1 - self.stop_pct)
                if new_stop > trailing_stop:
                    trailing_stop = new_stop

                # Sell if price breaches trailing stop
                if price < trailing_stop:
                    signals.iat[i] = "sell"
                    in_position = False
                    trailing_stop = None

        return signals
