# strategies/base_strategy.py

from abc import ABC
from typing import Callable, List, Optional

import pandas as pd

from algo_royale.strategies.strategy_filters.macd_bullish_cross import StrategyCondition


class Strategy(ABC):
    def __init__(
        self,
        filters: Optional[List[StrategyCondition]] = None,
        trend_funcs: Optional[List[Callable[[pd.DataFrame], pd.Series]]] = None,
        entry_funcs: Optional[List[Callable[[pd.DataFrame], pd.Series]]] = None,
        exit_funcs: Optional[List[Callable[[pd.DataFrame], pd.Series]]] = None,
    ):
        self.filters = filters or []
        self.trend_funcs = trend_funcs or []
        self.entry_funcs = entry_funcs or []
        self.exit_funcs = exit_funcs or []

    def _apply_filters(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies all filters to the DataFrame.
        Returns a boolean Series indicating where all filters are satisfied.
        """
        if not self.filters:
            return pd.Series(True, index=df.index)
        mask = pd.Series(True, index=df.index)
        for f in self.filters:
            mask &= f.apply(df)
        return mask

    def _apply_trend(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies trend confirmation functions to the DataFrame.
        Returns a boolean Series indicating where trend conditions are met.
        """
        if not self.trend_funcs:
            return pd.Series(True, index=df.index)
        mask = pd.Series(True, index=df.index)
        for func in self.trend_funcs:
            mask &= func(df)
        return mask

    def _apply_entry(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies entry conditions to the DataFrame.
        Returns a boolean Series indicating where entry conditions are met.
        """
        if not self.entry_funcs:
            return pd.Series(True, index=df.index)
        mask = pd.Series(True, index=df.index)
        for func in self.entry_funcs:
            mask &= func(df)
        return mask

    def _apply_exit(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies exit conditions to the DataFrame.
        Returns a boolean Series indicating where exit conditions are met.
        """
        if not self.exit_funcs:
            return pd.Series(False, index=df.index)
        mask = pd.Series(False, index=df.index)
        for func in self.exit_funcs:
            mask |= func(df)
        return mask

    def _apply_strategy(self, df: pd.DataFrame) -> pd.Series:
        """
        Combines trend, entry, and exit logic to generate signals.
        """
        signals = pd.Series("hold", index=df.index, name="signal")
        trend_mask = self._apply_trend(df)
        entry_mask = self._apply_entry(df)
        exit_mask = self._apply_exit(df)

        signals[trend_mask & entry_mask] = "buy"
        signals[exit_mask] = "sell"
        return signals

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies filters and then the strategy, setting 'hold' where filters fail.
        """
        required_cols = set(self.required_columns)
        for func in self.trend_funcs + self.entry_funcs + self.exit_funcs:
            if hasattr(func, "required_columns"):
                required_cols.update(func.required_columns)
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        mask = self._apply_filters(df)
        signals = self._apply_strategy(df)
        # Set signals to 'hold' where mask is False
        return signals.where(mask, other="hold")
