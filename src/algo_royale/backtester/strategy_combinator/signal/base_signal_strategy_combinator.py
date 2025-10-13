from typing import Type

from algo_royale.backtester.strategy.signal.base_signal_strategy import (
    BaseSignalStrategy,
)


class SignalStrategyCombinator:
    @classmethod
    def all_strategy_combinations(
        cls,
        logger=None,
        max_filter=1,
        max_entry=1,
        max_trend=1,
        max_exit=1,
        max_stateful_logic=1,
        **kwargs,
    ):
        # Get all possible conditions for each type
        filter_types = getattr(cls, "filter_condition_types", [None])
        entry_types = getattr(cls, "entry_condition_types", [None])
        trend_types = getattr(cls, "trend_condition_types", [None])
        exit_types = getattr(cls, "exit_condition_types", [None])
        stateful_types = getattr(cls, "stateful_logic_types", [None])

        def get_conditions(types, logger, max_count, allow_empty):
            conds = []
            for t in types:
                if hasattr(t, "all_possible_conditions"):
                    try:
                        # Some all_possible_conditions require logger, some don't
                        try:
                            c = t.all_possible_conditions(logger)
                        except TypeError:
                            c = t.all_possible_conditions()
                        conds.extend(c)
                    except Exception:
                        continue
            conds = conds[:max_count]
            if allow_empty:
                conds = conds + [None]
            return conds

        filter_conds = get_conditions(
            filter_types, logger, max_filter, getattr(cls, "allow_empty_filter", False)
        )
        entry_conds = get_conditions(
            entry_types, logger, max_entry, getattr(cls, "allow_empty_entry", False)
        )
        trend_conds = get_conditions(
            trend_types, logger, max_trend, getattr(cls, "allow_empty_trend", False)
        )
        exit_conds = get_conditions(
            exit_types, logger, max_exit, getattr(cls, "allow_empty_exit", False)
        )
        stateful_conds = get_conditions(
            stateful_types,
            logger,
            max_stateful_logic,
            getattr(cls, "allow_empty_stateful_logic", False),
        )
        if not stateful_conds:
            stateful_conds = [None]

        from itertools import product

        strategy_class = getattr(cls, "strategy_class", None)
        for f, e, t, x, s in product(
            filter_conds, entry_conds, trend_conds, exit_conds, stateful_conds
        ):

            def make_strategy(f=f, e=e, t=t, x=x, s=s):
                kwargs = {}
                if f is not None:
                    kwargs["filter_condition_types"] = [f]
                if e is not None:
                    kwargs["entry_condition_types"] = [e]
                if t is not None:
                    kwargs["trend_condition_types"] = [t]
                if x is not None:
                    kwargs["exit_condition_types"] = [x]
                if s is not None:
                    kwargs["stateful_logic_types"] = [s]
                return strategy_class(**kwargs) if strategy_class else None

            yield make_strategy

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
