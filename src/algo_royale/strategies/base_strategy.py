# strategies/base_strategy.py

from abc import ABC
from typing import List, Optional

import pandas as pd

from algo_royale.strategies.conditions.base_strategy_condition import StrategyCondition


class Strategy(ABC):
    """
    Base class for trading strategies.
    This class provides a framework for implementing trading strategies
    using modular functions for trend, entry, exit, and filter conditions.
    It allows for flexible composition of conditions to generate trading signals.
    Parameters:
    - filter_conditions: List of conditions to filter the DataFrame before applying the strategy.
    - trend_conditions: List of conditions to determine the trend direction.
    - entry_conditions: List of conditions to determine entry points for trades.
    - exit_conditions: List of conditions to determine exit points for trades.
    """

    def __init__(
        self,
        filter_conditions: Optional[List[StrategyCondition]] = None,
        trend_conditions: Optional[List[StrategyCondition]] = None,
        entry_conditions: Optional[List[StrategyCondition]] = None,
        exit_conditions: Optional[List[StrategyCondition]] = None,
    ):
        self.filter_conditions = filter_conditions or []
        self.trend_conditions = trend_conditions or []
        self.entry_conditions = entry_conditions or []
        self.exit_conditions = exit_conditions or []

    def _apply_filters(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies filter conditions to the DataFrame.
        Returns a boolean Series indicating where filter conditions are met.
        """
        if not self.filter_conditions:
            return pd.Series(True, index=df.index)
        mask = pd.Series(True, index=df.index)
        for f in self.filter_conditions:
            mask &= f.apply(df)
        return mask

    def _apply_trend(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies trend conditions to the DataFrame.
        Returns a boolean Series indicating where trend conditions are met.
        """
        if not self.trend_conditions:
            return pd.Series(True, index=df.index)
        mask = pd.Series(True, index=df.index)
        for func in self.trend_conditions:
            mask &= func(df)
        return mask

    def _apply_entry(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies entry conditions to the DataFrame.
        Returns a boolean Series indicating where entry conditions are met.
        """
        if not self.entry_conditions:
            return pd.Series(True, index=df.index)
        mask = pd.Series(True, index=df.index)
        for func in self.entry_conditions:
            mask &= func(df)
        return mask

    def _apply_exit(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies exit conditions to the DataFrame.
        Returns a boolean Series indicating where exit conditions are met.
        """
        if not self.exit_conditions:
            return pd.Series(False, index=df.index)
        mask = pd.Series(False, index=df.index)
        for func in self.exit_conditions:
            mask |= func(df)
        return mask

    def _apply_strategy(self, df: pd.DataFrame) -> pd.Series:
        """
        Applies the strategy logic to the DataFrame.
        Returns a Series with 'buy', 'sell', or 'hold' signals.
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
        Generates trading signals based on the strategy's conditions.
        Parameters:
        - df: DataFrame containing the price data with required columns.
        Returns:
        - signals: Series with 'buy', 'sell', or 'hold' signals.
        Raises:
        - ValueError: If required columns are missing in the DataFrame.
        """
        required_cols = set(self.required_columns)
        for func in (
            self.trend_conditions + self.entry_conditions + self.exit_conditions
        ):
            if hasattr(func, "required_columns"):
                required_cols.update(func.required_columns)
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        mask = self._apply_filters(df)
        signals = self._apply_strategy(df)
        # Set signals to 'hold' where mask is False
        return signals.where(mask, other="hold")
