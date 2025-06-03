import itertools


class StrategyCombinator:
    """
    Base class to generate all combinations of entry, trend, exit conditions and stateful logic.
    Subclass and set the class attributes below to lists of types/classes that implement
    all_possible_conditions().
    """

    filter_condition_types = [None]
    entry_condition_types = [None]
    trend_condition_types = [None]
    exit_condition_types = [None]
    stateful_logic_types = [None]
    strategy_class = None

    @classmethod
    def all_strategy_combinations(
        cls, max_filter=2, max_entry=2, max_trend=2, max_exit=2
    ):
        # Gather all possible conditions from each type
        filter_variants = []
        for cond_type in cls.filter_condition_types:
            filter_variants.extend(list(cond_type.all_possible_conditions()))
        entry_variants = []
        for cond_type in cls.entry_condition_types:
            entry_variants.extend(list(cond_type.all_possible_conditions()))
        trend_variants = []
        for cond_type in cls.trend_condition_types:
            trend_variants.extend(list(cond_type.all_possible_conditions()))
        exit_variants = []
        for cond_type in cls.exit_condition_types:
            exit_variants.extend(list(cond_type.all_possible_conditions()))
        stateful_logics = []
        for logic_type in cls.stateful_logic_types:
            stateful_logics.extend(list(logic_type.all_possible_conditions()))

        # Generate all non-empty combinations up to max_* for entry/trend/exit conditions
        def combos(variants, max_n, allow_empty=True):
            result = []
            for r in range(0 if allow_empty else 1, min(max_n, len(variants)) + 1):
                for combo in itertools.combinations(variants, r):
                    result.append(list(combo))
            if allow_empty and [] not in result:
                result.append([])
            return result

        filter_combos = combos(filter_variants, max_filter, allow_empty=True)
        entry_combos = combos(entry_variants, max_entry, allow_empty=True)
        trend_combos = combos(trend_variants, max_trend, allow_empty=False)
        exit_combos = combos(exit_variants, max_exit, allow_empty=True)

        strategies = []
        for filter_ in filter_combos:
            for entry in entry_combos:
                for trend in trend_combos:
                    for exit_ in exit_combos:
                        for stateful_logic in stateful_logics:
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
                            strategies.append(cls.strategy_class(**kwargs))
        return strategies
