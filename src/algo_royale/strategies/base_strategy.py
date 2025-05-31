# strategies/base_strategy.py

from typing import List, Optional

import pandas as pd

from algo_royale.strategies.strategy_filters.macd_bullish_cross import StrategyFilter


class Strategy:
    def __init__(self, filters: Optional[List[StrategyFilter]] = None):
        self.filters = filters or []

    def apply_filters(self, df: pd.DataFrame) -> pd.Series:
        if not self.filters:
            return pd.Series(True, index=df.index)
        mask = pd.Series(True, index=df.index)
        for f in self.filters:
            mask &= f.apply(df)
        return mask

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
