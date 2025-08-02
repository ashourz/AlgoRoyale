from typing import Optional

from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enum.signal_type import SignalType
from algo_royale.backtester.strategy.base_strategy import BaseStrategy
from algo_royale.backtester.strategy.signal.buffered_components.buffered_condition import (
    BufferedStrategyCondition,
)
from algo_royale.backtester.strategy.signal.buffered_components.buffered_stateful_logic import (
    BufferedStatefulLogic,
)
from algo_royale.logging.loggable import Loggable


class BufferedSignalStrategy(BaseStrategy):
    """
    Generic buffered strategy for live/tick data.
    Accepts buffered filter, trend, entry, exit conditions and buffered stateful logic.
    Mirrors BaseSignalStrategy logic but operates row-by-row using buffers.
    """

    def __init__(
        self,
        logger: Loggable,
        filter_conditions: Optional[list[BufferedStrategyCondition]] = None,
        trend_conditions: Optional[list[BufferedStrategyCondition]] = None,
        entry_conditions: Optional[list[BufferedStrategyCondition]] = None,
        exit_conditions: Optional[list[BufferedStrategyCondition]] = None,
        stateful_logic: Optional[BufferedStatefulLogic] = None,
    ):
        self.logger = logger
        self.filter_conditions = filter_conditions or []
        self.trend_conditions = trend_conditions or []
        self.entry_conditions = entry_conditions or []
        self.exit_conditions = exit_conditions or []
        self.stateful_logic = stateful_logic

    @property
    def required_columns(self) -> list[str]:
        required = set()
        for cond_list in [
            self.filter_conditions,
            self.trend_conditions,
            self.entry_conditions,
            self.exit_conditions,
        ]:
            for cond in cond_list:
                if hasattr(cond, "required_columns"):
                    required.update(cond.required_columns)
        if self.stateful_logic and hasattr(self.stateful_logic, "required_columns"):
            required.update(self.stateful_logic.required_columns)
        return list(required)

    def update(self, row: dict) -> dict:
        """
        Update the strategy with a new row (dict or pd.Series), applying buffered conditions and stateful logic.
        Returns a dict with ENTRY_SIGNAL and EXIT_SIGNAL for the row.
        """
        # Apply filter mask
        filter_mask = (
            all(cond.update(row) for cond in self.filter_conditions)
            if self.filter_conditions
            else True
        )
        # Apply trend mask
        trend_mask = (
            all(cond.update(row) for cond in self.trend_conditions)
            if self.trend_conditions
            else True
        )
        # Entry signal
        entry_signal = None
        for cond in self.entry_conditions:
            sig = cond.update(row)
            if sig:
                entry_signal = sig
                break
        if entry_signal is None:
            entry_signal = SignalType.HOLD.value
        # Exit signal
        exit_signal = None
        for cond in self.exit_conditions:
            sig = cond.update(row)
            if sig:
                exit_signal = sig
                break
        if exit_signal is None:
            exit_signal = SignalType.HOLD.value

        # Only allow entry if filter and trend masks are True
        if not (filter_mask and trend_mask):
            entry_signal = SignalType.HOLD.value

        # Stateful logic
        if self.stateful_logic:
            result = self.stateful_logic.update(
                row,
                entry_signal=entry_signal,
                exit_signal=exit_signal,
                trend_mask=trend_mask,
                filter_mask=filter_mask,
            )
            # If result is a dict, extract signals
            if isinstance(result, dict):
                entry_signal = result.get("entry_signal", entry_signal)
                exit_signal = result.get("exit_signal", exit_signal)

        return {
            SignalStrategyColumns.ENTRY_SIGNAL: entry_signal,
            SignalStrategyColumns.EXIT_SIGNAL: exit_signal,
        }

    def reset(self):
        """
        Reset all buffers and stateful logic.
        """
        for cond_list in [
            self.filter_conditions,
            self.trend_conditions,
            self.entry_conditions,
            self.exit_conditions,
        ]:
            for cond in cond_list:
                if hasattr(cond, "reset"):
                    cond.reset()
        if self.stateful_logic and hasattr(self.stateful_logic, "reset"):
            self.stateful_logic.reset()
