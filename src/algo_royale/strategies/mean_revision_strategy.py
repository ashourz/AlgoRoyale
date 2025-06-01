import pandas as pd

from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.price_above_sma import PriceAboveSMACondition


class MeanReversionStrategy(Strategy):
    """
    Mean Reversion Strategy with trailing stop, profit target, trend filter, and re-entry cooldown.
    This strategy identifies mean reversion opportunities based on the deviation of the price
    from a Simple Moving Average (SMA). It enters trades when the price deviates significantly
    from the SMA and exits based on a trailing stop, profit target, or reversion to the mean.
    The strategy uses a trend condition to filter trades, ensuring that trades are only taken
    when the price is above a specified SMA, indicating a bullish trend.
    Args:
        close_col (str): Column name for the close price.
        sma_col (str): Column name for the SMA values.
        window (int): Window size for the SMA.
        threshold (float): Deviation threshold to trigger buy/sell signals.
        stop_pct (float): Percentage for trailing stop loss.
        profit_target_pct (float): Percentage for profit target.
        reentry_cooldown (int): Number of periods to wait before re-entering after an exit.
    """

    def __init__(
        self,
        close_col: str = "close",
        sma_col: str = "sma_200",
        window: int = 20,
        threshold: float = 0.02,
        stop_pct: float = 0.02,
        profit_target_pct: float = 0.04,
        reentry_cooldown: int = 5,
    ):
        self.close_col = close_col
        self.window = window
        self.threshold = threshold
        self.stop_pct = stop_pct
        self.profit_target_pct = profit_target_pct
        self.trend_condition = [
            PriceAboveSMACondition(price_col=close_col, sma_col=sma_col)
        ]
        self.reentry_cooldown = reentry_cooldown

        super().__init__(trend_conditions=self.trend_conditions)

    def _apply_strategy(self, df: pd.DataFrame) -> pd.Series:
        ma = df[self.close_col].rolling(window=self.window, min_periods=1).mean()
        deviation = (df[self.close_col] - ma) / ma
        signals = pd.Series("hold", index=df.index, name="signal").copy()

        in_position = False
        entry_price = None
        trailing_stop = None
        last_exit_idx = -self.reentry_cooldown - 1

        # Use modular trend conditions
        trend_mask = self._apply_trend(df)

        for i in range(len(df)):
            price = df.iloc[i][self.close_col]
            dev = deviation.iloc[i]
            trend_ok = trend_mask.iloc[i]

            if not in_position:
                if (i - last_exit_idx) > self.reentry_cooldown:
                    if dev < -self.threshold and trend_ok:
                        signals.iloc[i] = "buy"
                        in_position = True
                        entry_price = price
                        trailing_stop = price * (1 - self.stop_pct)
            else:
                trailing_stop = max(trailing_stop, price * (1 - self.stop_pct))
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
