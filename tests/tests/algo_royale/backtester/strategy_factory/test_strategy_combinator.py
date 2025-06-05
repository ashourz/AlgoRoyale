from logging import Logger

from algo_royale.strategy_factory.combinator.base_strategy_combinator import (
    StrategyCombinator,
)


class DummyCondition:
    @staticmethod
    def all_possible_conditions(logger: Logger):
        # Return two dummy conditions
        return ["cond1", "cond2"]


class DummyStatefulLogic:
    @staticmethod
    def all_possible_conditions():
        return ["logic1"]


class DummyStrategy:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class DummyLogger:
    def info(self, msg, *args):
        print(msg % args)


def make_combinator(
    filter_types=[DummyCondition],
    entry_types=[DummyCondition],
    trend_types=[DummyCondition],
    exit_types=[DummyCondition],
    stateful_types=[DummyStatefulLogic],
    allow_empty_filter=False,
    allow_empty_entry=False,
    allow_empty_trend=False,
    allow_empty_exit=False,
    allow_empty_stateful_logic=False,
):
    class TestCombinator(StrategyCombinator):
        pass

    TestCombinator.filter_condition_types = filter_types
    TestCombinator.allow_empty_filter = allow_empty_filter
    TestCombinator.entry_condition_types = entry_types
    TestCombinator.allow_empty_entry = allow_empty_entry
    TestCombinator.trend_condition_types = trend_types
    TestCombinator.allow_empty_trend = allow_empty_trend
    TestCombinator.exit_condition_types = exit_types
    TestCombinator.allow_empty_exit = allow_empty_exit
    TestCombinator.stateful_logic_types = stateful_types
    TestCombinator.allow_empty_stateful_logic = allow_empty_stateful_logic
    TestCombinator.strategy_class = DummyStrategy
    return TestCombinator


def test_all_strategy_combinations_basic():
    Combinator = make_combinator()
    combos = list(
        Combinator.all_strategy_combinations(
            logger=DummyLogger(),
            max_filter=2,
            max_entry=2,
            max_trend=2,
            max_exit=2,
        )
    )
    assert (
        len(combos) == 81
    )  # 3*3*3*3*1 = 81 (if empty not allowed, 2^4*1=16 if only singles)
    assert all(callable(c) for c in combos)
    for c in combos:
        strat = c()
        assert isinstance(strat, DummyStrategy)


def test_all_strategy_combinations_with_empty_allowed():
    Combinator = make_combinator(
        allow_empty_filter=True,
        allow_empty_entry=True,
        allow_empty_trend=True,
        allow_empty_exit=True,
        allow_empty_stateful_logic=True,
    )
    combos = list(
        Combinator.all_strategy_combinations(
            logger=DummyLogger(),
            max_filter=2,
            max_entry=2,
            max_trend=2,
            max_exit=2,
        )
    )
    assert len(combos) == 512  # 4*4*4*4*2 = 512 (if 2 of each type, empty allowed)
    assert all(callable(c) for c in combos)
    for c in combos:
        strat = c()
        assert isinstance(strat, DummyStrategy)


def test_all_strategy_combinations_with_max_limits():
    Combinator = make_combinator()
    combos = list(
        Combinator.all_strategy_combinations(
            logger=DummyLogger(), max_filter=1, max_entry=1, max_trend=1, max_exit=1
        )
    )
    assert len(combos) == 16  # matches actual output
    assert all(callable(c) for c in combos)
    for c in combos:
        strat = c()
        assert isinstance(strat, DummyStrategy)


def test_all_strategy_combinations_empty_conditions():
    Combinator = make_combinator(
        filter_types=[],
        entry_types=[],
        trend_types=[],
        exit_types=[],
        stateful_types=[],
        allow_empty_filter=True,
        allow_empty_entry=True,
        allow_empty_trend=True,
        allow_empty_exit=True,
        allow_empty_stateful_logic=True,
    )
    combos = list(Combinator.all_strategy_combinations(logger=DummyLogger()))
    # Only one possible strategy: all empty
    assert len(combos) == 1
    strat_lambda = combos[0]
    assert callable(strat_lambda)
    strat = strat_lambda()
    assert isinstance(strat, DummyStrategy)
