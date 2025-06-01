from typing import List, Optional

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MomentumStrategy(Strategy):
    """
    Enhanced Momentum Strategy:
    - Calculates momentum as percent change over a lookback period.
    - Uses a threshold to avoid small noisy signals.
    - Optionally smooths momentum using a moving average.
    - Optionally requires confirmation over consecutive periods before signaling buy/sell.
    """

    def __init__(
        self,
        close_col: str = "close",
        lookback: int = 10,
        threshold: float = 0.0,
        smooth_window: Optional[int] = None,
        confirmation_periods: int = 1,
    ):
        if lookback <= 0:
            raise ValueError("lookback must be positive")
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        if confirmation_periods <= 0:
            raise ValueError("confirmation_periods must be positive")
        if smooth_window is not None and smooth_window <= 0:
            raise ValueError("smooth_window must be positive if specified")

        self.close_col = close_col
        self.lookback = lookback
        self.threshold = threshold
        self.smooth_window = smooth_window
        self.confirmation_periods = confirmation_periods

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        # Calculate raw momentum as percent change over lookback
        momentum = df[self.close_col].pct_change(periods=self.lookback)

        # Optional smoothing of momentum to reduce noise
        if self.smooth_window:
            momentum = momentum.rolling(window=self.smooth_window, min_periods=1).mean()

        # Prepare empty signals series defaulting to 'hold'
        signals = pd.Series("hold", index=df.index)

        # Determine buy/sell conditions based on threshold
        buy_condition = momentum > self.threshold
        sell_condition = momentum < -self.threshold

        # Confirmation logic: require momentum condition to hold for confirmation_periods consecutively
        if self.confirmation_periods > 1:
            # Rolling window of length confirmation_periods to check consecutive True values
            buy_confirmed = (
                buy_condition.rolling(window=self.confirmation_periods)
                .apply(lambda x: x.all(), raw=True)
                .fillna(0)
                .astype(bool)
            )
            sell_confirmed = (
                sell_condition.rolling(window=self.confirmation_periods)
                .apply(lambda x: x.all(), raw=True)
                .fillna(0)
                .astype(bool)
            )
        else:
            buy_confirmed = buy_condition
            sell_confirmed = sell_condition

        # Assign signals based on confirmed conditions
        signals[buy_confirmed] = "buy"
        signals[sell_confirmed] = "sell"

        return signals

    def get_required_columns(self) -> List[str]:
        return [self.close_col]

    def get_min_data_points(self) -> int:
        # Minimum points needed for momentum + smoothing + confirmation
        min_points = self.lookback + 1
        if self.smooth_window:
            min_points += self.smooth_window - 1
        if self.confirmation_periods > 1:
            min_points += self.confirmation_periods - 1
        return min_points
