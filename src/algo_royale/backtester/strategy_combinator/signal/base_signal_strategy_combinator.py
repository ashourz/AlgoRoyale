from algo_royale.backtester.strategy_combinator.base_strategy_combinator import (
    BaseStrategyCombinator,
)


class SignalStrategyCombinator(BaseStrategyCombinator):
    """
    Base class to generate all combinations of entry, trend, exit conditions and stateful logic.
    Subclass and set the class attributes below to lists of types/classes that implement
    all_possible_conditions().
    """

    filter_condition_types = [None]
    allow_empty_filter = False
    entry_condition_types = [None]
    allow_empty_entry = False
    trend_condition_types = [None]
    allow_empty_trend = False
    exit_condition_types = [None]
    allow_empty_exit = False
    stateful_logic_types = [None]
    allow_empty_stateful_logic = False
    strategy_class = None

    @classmethod
    def get_condition_types(cls):
        """Return the condition types for this combinator class."""
        return {
            "filter": cls.filter_condition_types or [],
            "entry": cls.entry_condition_types or [],
            "trend": cls.trend_condition_types or [],
            "exit": cls.exit_condition_types or [],
            "stateful_logic": cls.stateful_logic_types[0]
            if cls.stateful_logic_types
            else None,
        }
