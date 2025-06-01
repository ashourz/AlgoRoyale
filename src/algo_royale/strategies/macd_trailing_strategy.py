import pandas as pd

from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.sma_trend import SMATrendCondition


class MACDTrailingStopStrategy(Strategy):
    """
    MACD Strategy with Trailing Stop and Modular Trend Conditions.

    Buy when MACD crosses above signal line AND all trend conditions are met.
    Sell when MACD crosses below signal line OR trailing stop triggers.
    """

    def __init__(
        self,
        close_col="close",
        sma_fast_col="sma_50",
        sma_slow_col="sma_200",
        fast=12,
        slow=26,
        signal=9,
        stop_pct=0.02,
    ):
        self.close_col = close_col
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.stop_pct = stop_pct
        # Store the condition(s) as attributes
        self.trend_conditions = [
            SMATrendCondition(sma_fast_col=sma_fast_col, sma_slow_col=sma_slow_col)
        ]

        # Pass to base class
        super().__init__(trend_funcs=self.trend_conditions)

    def _apply_strategy(self, df: pd.DataFrame) -> pd.Series:
        """
        Apply the MACD strategy with trailing stop and modular trend conditions.
        Parameters:
        - df: DataFrame containing the price data with a 'close' column.
        Returns:
        - signals: Series with 'buy', 'sell', or 'hold' signals.
        """
        exp1 = df[self.close_col].ewm(span=self.fast, adjust=False).mean()
        exp2 = df[self.close_col].ewm(span=self.slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()

        signals = pd.Series("hold", index=df.index, name="signal")
        macd_prev = macd.shift(1)
        signal_prev = signal_line.shift(1)

        in_position = False
        trailing_stop = None

        # Use modular trend conditions
        trend_mask = self._apply_trend(df)

        for i in range(len(df)):
            if pd.isna(macd.iloc[i]) or pd.isna(signal_line.iloc[i]):
                continue

            price = df.iloc[i][self.close_col]
            trend_ok = trend_mask.iloc[i]

            if not in_position:
                buy_signal = (macd_prev.iloc[i] < signal_prev.iloc[i]) and (
                    macd.iloc[i] > signal_line.iloc[i]
                )
                if buy_signal and trend_ok:
                    signals.iloc[i] = "buy"
                    in_position = True
                    trailing_stop = price * (1 - self.stop_pct)
            else:
                trailing_stop = max(trailing_stop, price * (1 - self.stop_pct))
                sell_signal = (macd_prev.iloc[i] > signal_prev.iloc[i]) and (
                    macd.iloc[i] < signal_line.iloc[i]
                )
                if sell_signal or price < trailing_stop:
                    signals.iloc[i] = "sell"
                    in_position = False
                    trailing_stop = None

        return signals
