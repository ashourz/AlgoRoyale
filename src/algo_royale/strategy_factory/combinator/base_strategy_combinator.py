import inspect
import itertools
from abc import ABC
from logging import Logger
from typing import Callable, Generator

from algo_royale.strategy_factory.strategies.base_strategy import Strategy


class StrategyCombinator(ABC):
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
    def all_strategy_combinations(
        cls, logger: Logger, max_filter=1, max_entry=1, max_trend=1, max_exit=1
    ) -> Generator[Callable[[], Strategy], None, None]:
        """
        Generate all possible strategy combinations based on the defined condition types.
        This method combines all possible conditions from the specified types and generates
        all non-empty combinations up to the specified maximums for each condition type.
        Parameters:
            max_filter (int): Maximum number of filter conditions to combine.
            max_entry (int): Maximum number of entry conditions to combine.
            max_trend (int): Maximum number of trend conditions to combine.
            max_exit (int): Maximum number of exit conditions to combine.
        Returns:
            list: A list of Strategy instances representing all possible combinations.
        """
        # Gather all possible conditions from each type
        logger.info(
            "Generating all strategy combinations with max_filter=%d, max_entry=%d, "
            "max_trend=%d, max_exit=%d",
            max_filter,
            max_entry,
            max_trend,
            max_exit,
        )
        filter_variants = []
        for cond_type in cls.filter_condition_types:
            filter_variants.extend(
                list(cond_type.all_possible_conditions(logger=logger))
            )
        entry_variants = []
        for cond_type in cls.entry_condition_types:
            entry_variants.extend(
                list(cond_type.all_possible_conditions(logger=logger))
            )
        trend_variants = []
        for cond_type in cls.trend_condition_types:
            trend_variants.extend(
                list(cond_type.all_possible_conditions(logger=logger))
            )
        exit_variants = []
        for cond_type in cls.exit_condition_types:
            exit_variants.extend(list(cond_type.all_possible_conditions(logger=logger)))
        stateful_logics = []
        for logic_type in cls.stateful_logic_types:
            stateful_logics.extend(list(logic_type.all_possible_conditions()))
        if cls.allow_empty_stateful_logic and [] not in stateful_logics:
            stateful_logics.append([])

        logger.info(
            "Found %d filter, %d entry, %d trend, %d exit, and %d stateful logic types",
            len(filter_variants),
            len(entry_variants),
            len(trend_variants),
            len(exit_variants),
            len(stateful_logics),
        )

        # Generate all non-empty combinations up to max_* for entry/trend/exit conditions
        def combos(variants, max_n, allow_empty=True):
            result = []
            for r in range(0 if allow_empty else 1, min(max_n, len(variants)) + 1):
                for combo in itertools.combinations(variants, r):
                    result.append(list(combo))
            if allow_empty and [] not in result:
                result.append([])
            return result

        filter_combos = combos(
            filter_variants, max_filter, allow_empty=cls.allow_empty_filter
        )
        entry_combos = combos(
            entry_variants, max_entry, allow_empty=cls.allow_empty_entry
        )
        trend_combos = combos(
            trend_variants, max_trend, allow_empty=cls.allow_empty_trend
        )
        exit_combos = combos(exit_variants, max_exit, allow_empty=cls.allow_empty_exit)
        # Generate all combinations of strategies
        logger.info(
            "Generating combinations of strategies with %d filter, %d entry, %d trend, %d exit, and %d stateful logic types",
            len(filter_combos),
            len(entry_combos),
            len(trend_combos),
            len(exit_combos),
            len(stateful_logics),
        )
        for filter_ in filter_combos:
            for entry in entry_combos:
                for trend in trend_combos:
                    for exit_ in exit_combos:
                        for stateful_logic in stateful_logics:
                            try:
                                kwargs = {
                                    "filter_conditions": filter_,
                                    "entry_conditions": entry,
                                    "trend_conditions": trend,
                                    "exit_conditions": exit_,
                                    "stateful_logic": stateful_logic,
                                }
                                # Remove empty lists if the strategy doesn't accept them
                                if not filter_:
                                    kwargs.pop("filter_conditions")
                                if not entry:
                                    kwargs.pop("entry_conditions")
                                if not trend:
                                    kwargs.pop("trend_conditions")
                                if not exit_:
                                    kwargs.pop("exit_conditions")
                                # If the strategy class does not accept stateful logic, remove it
                                if (
                                    not stateful_logic
                                    and not cls.allow_empty_stateful_logic
                                ):
                                    kwargs.pop("stateful_logic")
                                # If the strategy class does not accept any of the conditions, skip it
                                init_params = inspect.signature(
                                    cls.strategy_class.__init__
                                ).parameters
                                accepted_keys = set(init_params.keys()) - {"self"}

                                filtered_kwargs = {
                                    k: v
                                    for k, v in kwargs.items()
                                    if k in accepted_keys
                                }
                                # Yield a partial (lambda) that will instantiate the strategy when called
                                from functools import partial

                                yield partial(cls.strategy_class, **filtered_kwargs)
                            except Exception as e:
                                logger.error(
                                    "Error creating strategy with filter=%s, entry=%s, "
                                    "trend=%s, exit=%s, stateful_logic=%s: %s",
                                    filter_,
                                    entry,
                                    trend,
                                    exit_,
                                    stateful_logic,
                                    e,
                                )
