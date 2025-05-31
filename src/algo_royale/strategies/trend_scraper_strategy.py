import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class TrendScraperStrategy(Strategy):
    def __init__(
        self,
        ema_col: str = "ema_20",
        sma_col: str = "sma_20",
        return_col: str = "log_return",
        volatility_col: str = "volatility_20",
        range_col: str = "range",
        trend_confirm_window: int = 3,
        exit_threshold: float = -0.005,
    ):
        self.ema_col = ema_col
        self.sma_col = sma_col
        self.return_col = return_col
        self.volatility_col = volatility_col
        self.range_col = range_col
        self.trend_confirm_window = trend_confirm_window
        self.exit_threshold = exit_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series("hold", index=df.index, name="signal")

        # Validate required columns
        required = [
            self.ema_col,
            self.sma_col,
            self.return_col,
            self.volatility_col,
            self.range_col,
        ]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Step 1: Identify Uptrend
        df["trend_confirmed"] = (df[self.ema_col] > df[self.sma_col]) & (
            df[self.ema_col] > df[self.ema_col].shift(1)
        )
        df["uptrend"] = (
            df["trend_confirmed"].rolling(window=self.trend_confirm_window).sum()
            == self.trend_confirm_window
        )

        # Step 2: Identify Weakness or Downturn
        weakness = df[self.return_col] < self.exit_threshold
        volatility_spike = df[self.range_col] > df[self.volatility_col]

        # Step 3: Apply Signal Logic
        signals[df["uptrend"]] = "buy"
        signals[weakness | volatility_spike] = "sell"

        return signals
