from typing import Type

from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)


class SignalStrategyCombinator:
    """
    Base class to generate all combinations of entry, trend, exit conditions and stateful logic.
    Subclass and set the class attributes below to lists of types/classes that implement
    all_possible_conditions().
    """

    def __init__(
        self,
        strategy_class: Type[BaseSignalStrategy],
        filter_condition_types: list[type] = [None],
        entry_condition_types: list[type] = [None],
        trend_condition_types: list[type] = [None],
        exit_condition_types: list[type] = [None],
        stateful_logic_types: list[type] = [None],
    ):
        self.strategy_class = strategy_class
        self.filter_condition_types = filter_condition_types
        self.entry_condition_types = entry_condition_types
        self.trend_condition_types = trend_condition_types
        self.exit_condition_types = exit_condition_types
        self.stateful_logic_types = stateful_logic_types

    def get_condition_types(self):
        """Return the condition types for this combinator class."""
        return {
            "filter": self.filter_condition_types or [],
            "entry": self.entry_condition_types or [],
            "trend": self.trend_condition_types or [],
            "exit": self.exit_condition_types or [],
            "stateful_logic": self.stateful_logic_types[0]
            if self.stateful_logic_types
            else None,
        }
