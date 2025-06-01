import pandas as pd

from .base_stateful_logic import StatefulLogic


class MACDTrailingStatefulLogic(StatefulLogic):
    def __init__(self, close_col, fast, slow, signal, stop_pct):
        self.close_col = close_col
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.stop_pct = stop_pct

    def __call__(self, i, df, signals, state, trend_mask, entry_mask, exit_mask):
        # Initialize state if empty
        if not state:
            state = {
                "in_position": False,
                "trailing_stop": None,
            }

        exp1 = df[self.close_col].ewm(span=self.fast, adjust=False).mean()
        exp2 = df[self.close_col].ewm(span=self.slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=self.signal, adjust=False).mean()
        macd_prev = macd.shift(1)
        signal_prev = signal_line.shift(1)

        # Skip if not enough data
        if pd.isna(macd.iloc[i]) or pd.isna(signal_line.iloc[i]):
            return signals.iloc[i], state

        price = df.iloc[i][self.close_col]
        trend_ok = trend_mask.iloc[i]

        if not state["in_position"]:
            buy_signal = (macd_prev.iloc[i] < signal_prev.iloc[i]) and (
                macd.iloc[i] > signal_line.iloc[i]
            )
            if buy_signal and trend_ok:
                signals.iloc[i] = "buy"
                state["in_position"] = True
                state["trailing_stop"] = price * (1 - self.stop_pct)
        else:
            state["trailing_stop"] = max(
                state["trailing_stop"], price * (1 - self.stop_pct)
            )
            sell_signal = (macd_prev.iloc[i] > signal_prev.iloc[i]) and (
                macd.iloc[i] < signal_line.iloc[i]
            )
            if sell_signal or price < state["trailing_stop"]:
                signals.iloc[i] = "sell"
                state["in_position"] = False
                state["trailing_stop"] = None

        return signals.iloc[i], state

    @property
    def required_columns(self):
        """
        Returns a list of required columns for this stateful logic.
        """
        return [self.close_col]
