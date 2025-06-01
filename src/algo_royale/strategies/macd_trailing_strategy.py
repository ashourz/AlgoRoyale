import pandas as pd

from algo_royale.strategies.base_strategy import Strategy


class MACDTrailingStopStrategy(Strategy):
    """
    MACD Strategy with Trailing Stop and Optional Trend Filter

    Buy when MACD crosses above signal line AND trend_filter (if any) allows entry.
    Sell when MACD crosses below signal line OR trailing stop triggers.
    """

    def __init__(
        self,
        close_col="close",
        fast=12,
        slow=26,
        signal=9,
        stop_pct=0.02,
        trend_filter_func=None,  # function(row) -> bool, trend confirmation
        trend_filter_col=None,  # column(s) used by trend_filter_func
    ):
        self.close_col = close_col
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.stop_pct = stop_pct
        self.trend_filter_func = trend_filter_func
        self.trend_filter_col = trend_filter_col

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        exp1 = df[self.close_col].ewm(span=self.fast, adjust=False).mean()
        exp2 = df[self.close_col].ewm(span=self.slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()

        signals = pd.Series("hold", index=df.index, name="signal")

        macd_prev = macd.shift(1)
        signal_prev = signal_line.shift(1)

        in_position = False
        trailing_stop = None

        for i in range(len(df)):
            if pd.isna(macd.iloc[i]) or pd.isna(signal_line.iloc[i]):
                # Insufficient data for MACD
                continue

            row = df.iloc[i]
            price = row[self.close_col]

            # Evaluate trend filter if provided
            trend_ok = True
            if self.trend_filter_func is not None and self.trend_filter_col is not None:
                # Pass the whole row for flexibility
                trend_ok = self.trend_filter_func(row)

            if not in_position:
                # Check for buy signal: MACD crossover up and trend filter passes
                buy_signal = (macd_prev.iloc[i] < signal_prev.iloc[i]) and (
                    macd.iloc[i] > signal_line.iloc[i]
                )
                if buy_signal and trend_ok:
                    signals.iloc[i] = "buy"
                    in_position = True
                    trailing_stop = price * (1 - self.stop_pct)
            else:
                # Update trailing stop to max between current and new stop price
                trailing_stop = max(trailing_stop, price * (1 - self.stop_pct))

                # Sell on MACD crossover down OR price below trailing stop
                sell_signal = (macd_prev.iloc[i] > signal_prev.iloc[i]) and (
                    macd.iloc[i] < signal_line.iloc[i]
                )
                if sell_signal or price < trailing_stop:
                    signals.iloc[i] = "sell"
                    in_position = False
                    trailing_stop = None

        return signals

    def get_required_columns(self):
        cols = [self.close_col]
        if self.trend_filter_col:
            if isinstance(self.trend_filter_col, list):
                cols.extend(self.trend_filter_col)
            else:
                cols.append(self.trend_filter_col)
        return list(set(cols))

    def get_min_data_points(self):
        return self.slow + self.signal
