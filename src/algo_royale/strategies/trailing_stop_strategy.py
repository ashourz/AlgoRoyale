import pandas as pd

from algo_royale.strategies.base_strategy import Strategy
from algo_royale.strategies.conditions.boolean_column_entry import (
    BooleanColumnEntryCondition,
)
from algo_royale.strategies.conditions.trend_above_sma import TrendAboveSMACondition


class TrailingStopStrategy(Strategy):
    def __init__(self, close_col: str = "close_price", stop_pct: float = 0.02):
        """
        Parameters:
        - close_col: column name for price data
        - stop_pct: trailing stop percentage (0 < stop_pct < 1)
        - entry_conditions: list of entry condition objects
        - trend_conditions: list of trend condition objects
        """
        if not (0 < stop_pct < 1):
            raise ValueError("stop_pct must be between 0 and 1")

        self.close_col = close_col
        self.stop_pct = stop_pct
        # Define and store condition objects
        self.entry_conditions = [BooleanColumnEntryCondition(entry_col="entry_signal")]
        self.trend_conditions = [
            TrendAboveSMACondition(price_col=close_col, sma_col="sma_200")
        ]

        super().__init__(
            entry_conditions=self.entry_conditions,
            trend_conditions=self.trend_conditions,
        )

    def _apply_strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series("hold", index=df.index, name="signal")
        in_position = False
        trailing_stop = None

        entry_mask = self._apply_entry(df)
        trend_mask = self._apply_trend(df)

        for i in range(len(df)):
            price = df.iloc[i][self.close_col]
            entry_signal = entry_mask.iloc[i]
            trend_ok = trend_mask.iloc[i]

            if not in_position:
                if entry_signal and trend_ok:
                    signals.iat[i] = "buy"
                    in_position = True
                    trailing_stop = price * (1 - self.stop_pct)
            else:
                new_stop = price * (1 - self.stop_pct)
                if new_stop > trailing_stop:
                    trailing_stop = new_stop
                if price < trailing_stop:
                    signals.iat[i] = "sell"
                    in_position = False
                    trailing_stop = None

        return signals
