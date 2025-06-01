import pandas as pd

from .base_strategy import Strategy


class VolumeSurgeStrategy(Strategy):
    """
    Volume Surge Strategy:
    - Buy when current volume exceeds a multiple of the moving average volume.
    - Sell on the next bar after the surge.
    - Hold otherwise.

    Parameters:
    - vol_col: column name for volume data (default "volume").
    - threshold: multiplier to define volume surge (default 2.0).
    - ma_window: window size for moving average of volume (default 20).
    """

    def __init__(
        self, vol_col: str = "volume", threshold: float = 2.0, ma_window: int = 20
    ):
        self.vol_col = vol_col
        self.threshold = threshold
        self.ma_window = ma_window

    def _strategy(self, df: pd.DataFrame) -> pd.Series:
        if self.vol_col not in df.columns:
            raise ValueError(f"DataFrame must contain '{self.vol_col}' column.")

        # Calculate moving average volume
        vol_ma = df[self.vol_col].rolling(window=self.ma_window, min_periods=1).mean()

        # Identify volume surge bars
        surge = df[self.vol_col] > (vol_ma * self.threshold)

        signals = pd.Series("hold", index=df.index, name="signal")

        # Buy signal when surge occurs
        signals.loc[surge] = "buy"

        # Sell signal on the next bar after a surge (exit after buying)
        signals.loc[surge.shift(-1).fillna(False)] = "sell"

        return signals
