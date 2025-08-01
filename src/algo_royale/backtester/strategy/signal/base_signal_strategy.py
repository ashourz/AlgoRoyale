# strategies/base_strategy.py

import hashlib
from typing import Optional

import pandas as pd

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enum.signal_type import SignalType
from algo_royale.backtester.strategy.base_strategy import BaseStrategy
from algo_royale.backtester.strategy.signal.conditions.base_strategy_condition import (
    StrategyCondition,
)
from algo_royale.backtester.strategy.signal.stateful_logic.base_stateful_logic import (
    StatefulLogic,
)
from algo_royale.logging.loggable import Loggable


class BaseSignalStrategy(BaseStrategy):
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
    - stateful_logic: Optional stateful logic to maintain state across rows.

    """

    def __init__(
        self,
        logger: Loggable,
        filter_conditions: Optional[list[StrategyCondition]] = None,
        trend_conditions: Optional[list[StrategyCondition]] = None,
        entry_conditions: Optional[list[StrategyCondition]] = None,
        exit_conditions: Optional[list[StrategyCondition]] = None,
        stateful_logic: Optional[StatefulLogic] = None,
    ):
        self.logger = logger
        self.filter_conditions = filter_conditions or []
        self.trend_conditions = trend_conditions or []
        self.entry_conditions = entry_conditions or []
        self.exit_conditions = exit_conditions or []
        self.stateful_logic = stateful_logic

    @property
    def required_columns(self) -> list[str]:
        """
        Returns a list of required columns for the strategy.
        This includes columns needed for trend, entry, exit, and filter conditions.
        """
        try:
            required = set()
            for func in (
                self.trend_conditions
                + self.entry_conditions
                + self.exit_conditions
                + ([self.stateful_logic] if self.stateful_logic is not None else [])
                + self.filter_conditions
            ):
                if hasattr(func, "required_columns"):
                    required.update(func.required_columns)
            return list(required)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in required_columns: {e}")
            return []

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
            if self.logger:
                self.logger.debug(
                    f"trend_condition type: {type(func)}"
                )  # Should always be a condition object, not a list
            mask &= func(df)
        return mask

    def _apply_entry(self, df: pd.DataFrame) -> pd.Series:
        if not self.entry_conditions:
            return pd.Series(SignalType.HOLD.value, index=df.index)
        # Combine entry signals (example: take first non-hold, or customize as needed)
        entry_signals = pd.Series(SignalType.HOLD.value, index=df.index)
        for cond in self.entry_conditions:
            if self.logger:
                self.logger.debug(f"entry_condition type: {type(cond)}")
            cond_signal = cond.apply(df)
            # If the condition returns boolean, map True to BUY, False to HOLD
            if cond_signal.dtype == bool:
                mapped = pd.Series(SignalType.HOLD.value, index=df.index)
                mapped[cond_signal] = SignalType.BUY.value
                cond_signal = mapped
            entry_signals = cond_signal.where(
                cond_signal != SignalType.HOLD.value, entry_signals
            )
            if self.logger:
                self.logger.debug(
                    f"Intermediate entry_signals: {entry_signals.unique()}"
                )
        return entry_signals

    def _apply_exit(self, df: pd.DataFrame) -> pd.Series:
        if not self.exit_conditions:
            return pd.Series(SignalType.HOLD.value, index=df.index)
        exit_signals = pd.Series(SignalType.HOLD.value, index=df.index)
        for cond in self.exit_conditions:
            if self.logger:
                self.logger.debug(f"exit_condition type: {type(cond)}")
            # Should always be a condition object, not a list
            cond_signal = cond.apply(df)
            # If the condition returns boolean, map True to SELL, False to HOLD
            if cond_signal.dtype == bool:
                mapped = pd.Series(SignalType.HOLD.value, index=df.index)
                mapped[cond_signal] = SignalType.SELL.value
                cond_signal = mapped
            exit_signals = cond_signal.where(
                cond_signal != SignalType.HOLD.value, exit_signals
            )
        return exit_signals

    def _apply_strategy(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies the strategy logic to the DataFrame.
        Generates entry and exit signals based on trend, entry, and exit conditions.
        Returns a DataFrame with ENTRY_SIGNAL and EXIT_SIGNAL columns.
        """
        trend_mask = self._apply_trend(df)
        entry_signals = self._apply_entry(df)
        exit_signals = self._apply_exit(df)
        filter_mask = self._apply_filters(df)

        # Only allow entry signals where both filter and trend masks are True
        entry_signals = entry_signals.where(
            filter_mask & trend_mask, other=SignalType.HOLD.value
        )

        # If stateful logic is present, apply it row by row
        if self.stateful_logic is not None:
            state = {}
            entry_signals_new = entry_signals.copy()
            exit_signals_new = exit_signals.copy()
            for i in range(len(df)):
                entry_signals_new.iloc[i], exit_signals_new.iloc[i], state = (
                    self.stateful_logic(
                        i=i,
                        df=df,
                        entry_signal=entry_signals.iloc[i],
                        exit_signal=exit_signals.iloc[i],
                        state=state,
                        trend_mask=trend_mask,
                        filter_mask=filter_mask,
                    )
                )
            entry_signals = entry_signals_new
            exit_signals = exit_signals_new

        result = df.copy()
        result[SignalStrategyColumns.ENTRY_SIGNAL] = entry_signals
        result[SignalStrategyColumns.EXIT_SIGNAL] = exit_signals
        return result

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # Ensure all required columns are numeric before any math
        for col in self.required_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        try:
            required_cols = set(self.required_columns)
            missing = required_cols - set(df.columns)
            if missing:
                df = df.copy()
                df[SignalStrategyColumns.ENTRY_SIGNAL] = SignalType.HOLD.value
                df[SignalStrategyColumns.EXIT_SIGNAL] = SignalType.HOLD.value
                return df
            if self.logger:
                self.logger.info(
                    f"Generating signals for strategy: {self.get_description()}"
                )
            filter_mask = self._apply_filters(df)
            self.logger.info(
                f"Filter mask sum: {filter_mask.sum()} / {len(filter_mask)}"
            )
            trend_mask = self._apply_trend(df)
            self.logger.info(f"Trend mask sum: {trend_mask.sum()} / {len(trend_mask)}")
            entry_signals = self._apply_entry(df)
            self.logger.info(f"Entry signals unique: {entry_signals.unique()}")
            exit_signals = self._apply_exit(df)

            # Only allow entry signals where both filter and trend masks are True
            entry_signals = entry_signals.where(
                filter_mask & trend_mask, other=SignalType.HOLD.value
            )

            # If stateful logic is present, apply it row by row
            if self.stateful_logic is not None:
                state = {}
                entry_signals_new = entry_signals.copy()
                exit_signals_new = exit_signals.copy()
                for i in range(len(df)):
                    entry_signals_new.iloc[i], exit_signals_new.iloc[i], state = (
                        self.stateful_logic(
                            i=i,
                            df=df,
                            entry_signal=entry_signals.iloc[i],
                            exit_signal=exit_signals.iloc[i],
                            state=state,
                            trend_mask=trend_mask,
                            filter_mask=filter_mask,
                        )
                    )
                entry_signals = entry_signals_new
                exit_signals = exit_signals_new

            df = df.copy()
            df[SignalStrategyColumns.ENTRY_SIGNAL] = entry_signals
            df[SignalStrategyColumns.EXIT_SIGNAL] = exit_signals
            return df
        except Exception as e:
            self.logger.error(f"Error generating signals: {e}")
            df = df.copy()
            df[SignalStrategyColumns.ENTRY_SIGNAL] = SignalType.HOLD.value
            df[SignalStrategyColumns.EXIT_SIGNAL] = SignalType.HOLD.value
            return df

    def get_description(self):
        def id_or_list(val):
            if isinstance(val, list):
                return [v.get_id() if hasattr(v, "get_id") else repr(v) for v in val]
            elif hasattr(val, "get_id"):
                return val.get_id()
            else:
                return repr(val)

        params = {
            "entry_conditions": id_or_list(self.entry_conditions),
            "exit_conditions": id_or_list(self.exit_conditions),
            "trend_conditions": id_or_list(self.trend_conditions),
            "filter_conditions": id_or_list(self.filter_conditions),
            "stateful_logic": id_or_list(self.stateful_logic),
        }
        param_str = ",".join(f"{k}={repr(v)}" for k, v in sorted(params.items()))
        return f"{self.__class__.__name__}({param_str})"

    def get_hash_id(self):
        """
        Returns the directory where this strategy is located.
        This can be used to load additional resources or configurations.
        """
        strategy_id = self.get_description()
        return hashlib.sha256(strategy_id.encode()).hexdigest()  # 64 hex chars
