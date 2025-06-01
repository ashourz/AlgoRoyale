from typing import Callable, List, Optional

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MeanReversionStrategy(Strategy):
    """
    Mean Reversion Strategy with trailing stop, profit target, trend filter, and re-entry cooldown.
    """

    def __init__(
        self,
        close_col: str = "close",
        window: int = 20,
        threshold: float = 0.02,
        stop_pct: float = 0.02,
        profit_target_pct: float = 0.04,
        trend_filter_func: Optional[Callable[[pd.Series], bool]] = None,
        trend_filter_col: Optional[str] = None,
        reentry_cooldown: int = 5,  # bars to wait before re-entry after a sell
    ):
        self.close_col = close_col
        self.window = window
        self.threshold = threshold
        self.stop_pct = stop_pct
        self.profit_target_pct = profit_target_pct
        self.trend_filter_func = trend_filter_func
        self.trend_filter_col = trend_filter_col
        self.reentry_cooldown = reentry_cooldown

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        ma = df[self.close_col].rolling(window=self.window, min_periods=1).mean()
        deviation = (df[self.close_col] - ma) / ma
        signals = pd.Series("hold", index=df.index, name="signal").copy()

        in_position = False
        entry_price = None
        trailing_stop = None
        last_exit_idx = -self.reentry_cooldown - 1  # initialize far in the past

        for i in range(len(df)):
            price = df.iloc[i][self.close_col]
            row = df.iloc[i]

            # Check trend filter (if provided)
            trend_ok = True
            if self.trend_filter_func is not None and self.trend_filter_col is not None:
                trend_ok = self.trend_filter_func(row)

            # Calculate deviation at this bar
            dev = deviation.iloc[i]

            if not in_position:
                # Only allow entry if cooldown is over
                if (i - last_exit_idx) > self.reentry_cooldown:
                    if dev < -self.threshold and trend_ok:
                        signals.iloc[i] = "buy"
                        in_position = True
                        entry_price = price
                        trailing_stop = price * (1 - self.stop_pct)
            else:
                # Update trailing stop (move up only)
                trailing_stop = max(trailing_stop, price * (1 - self.stop_pct))

                # Check exit conditions
                hit_stop = price < trailing_stop
                hit_profit = price >= entry_price * (1 + self.profit_target_pct)
                sell_signal = dev > self.threshold or hit_stop or hit_profit

                if sell_signal:
                    signals.iloc[i] = "sell"
                    in_position = False
                    entry_price = None
                    trailing_stop = None
                    last_exit_idx = i

        return signals

    def get_required_columns(self) -> List[str]:
        cols = [self.close_col]
        if self.trend_filter_col:
            if isinstance(self.trend_filter_col, list):
                cols.extend(self.trend_filter_col)
            else:
                cols.append(self.trend_filter_col)
        return list(set(cols))

    def get_min_data_points(self) -> int:
        return self.window
