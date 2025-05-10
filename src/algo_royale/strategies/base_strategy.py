# strategies/base_strategy.py

import pandas as pd


class Strategy:
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Given historical price data (DataFrame), return a list/series of trading signals.
        Each signal should be one of: 'buy', 'sell', or 'hold'.
        
        Parameters:
        - historical_data (pd.DataFrame): Must contain 'Close' prices at minimum.

        Returns:
        - signals (list or pd.Series): Trading signals aligned with historical_data dates.
        """
        raise NotImplementedError("generate_signals() must be implemented by subclass.")
