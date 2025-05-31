from typing import Callable, Optional

import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class TrendScraperStrategy(Strategy):
    """
    Trend Scraper Strategy with flexible trend confirmation and exit conditions.

    Buy when trend confirmation function returns True over a rolling window.
    Sell when exit condition function returns True.
    Hold otherwise.
    """

    def __init__(
        self,
        ema_col: str = "ema_20",
        sma_col: str = "sma_20",
        return_col: str = "log_return",
        volatility_col: str = "volatility_20",
        range_col: str = "range",
        trend_confirm_window: int = 3,
        exit_threshold: float = -0.005,
        # Optional custom functions for flexibility:
        trend_confirm_func: Optional[
            Callable[[pd.DataFrame, str, str], pd.Series]
        ] = None,
        exit_condition_func: Optional[
            Callable[[pd.DataFrame, str, str], pd.Series]
        ] = None,
    ):
        """
        Parameters:
        - ema_col, sma_col, return_col, volatility_col, range_col: columns for indicators.
        - trend_confirm_window: number of periods for rolling trend confirmation.
        - exit_threshold: threshold for returns to trigger exit if using default exit logic.
        - trend_confirm_func: function(df, ema_col, sma_col) -> pd.Series[bool], custom trend logic.
        - exit_condition_func: function(df, return_col, volatility_col) -> pd.Series[bool], custom exit logic.
        """
        self.ema_col = ema_col
        self.sma_col = sma_col
        self.return_col = return_col
        self.volatility_col = volatility_col
        self.range_col = range_col
        self.trend_confirm_window = trend_confirm_window
        self.exit_threshold = exit_threshold
        self.trend_confirm_func = trend_confirm_func
        self.exit_condition_func = exit_condition_func

    def _default_trend_confirm(self, df: pd.DataFrame) -> pd.Series:
        """Default trend confirmation: EMA above SMA and EMA rising."""
        return (df[self.ema_col] > df[self.sma_col]) & (
            df[self.ema_col] > df[self.ema_col].shift(1)
        )

    def _default_exit_condition(self, df: pd.DataFrame) -> pd.Series:
        """Default exit condition: return below threshold or volatility spike."""
        weakness = df[self.return_col] < self.exit_threshold
        volatility_spike = df[self.range_col] > df[self.volatility_col]
        return weakness | volatility_spike

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Validate required columns
        required_cols = {
            self.ema_col,
            self.sma_col,
            self.return_col,
            self.volatility_col,
            self.range_col,
        }
        missing_cols = required_cols - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        signals = pd.Series("hold", index=df.index, name="signal")

        # Trend confirmation
        trend_series = (
            self.trend_confirm_func(df, self.ema_col, self.sma_col)
            if self.trend_confirm_func is not None
            else self._default_trend_confirm(df)
        )
        # Rolling window check
        uptrend = (
            trend_series.rolling(window=self.trend_confirm_window).sum()
            == self.trend_confirm_window
        )

        # Exit condition
        exit_condition = (
            self.exit_condition_func(df, self.return_col, self.volatility_col)
            if self.exit_condition_func is not None
            else self._default_exit_condition(df)
        )

        signals.loc[uptrend] = "buy"
        signals.loc[exit_condition] = "sell"

        return signals
