from unittest.mock import MagicMock

from algo_royale.portfolio.combinator.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class DummyStrategy:
    __name__ = "DummyStrategy"

    def __init__(self, a=1):
        self.a = a

    @staticmethod
    def optuna_suggest(trial, prefix=""):
        return {"a": 42}


def test_all_strategy_combinations_default():
    combinator = PortfolioStrategyCombinator(DummyStrategy)
    combos = list(combinator.all_strategy_combinations())
    assert len(combos) == 1
    assert combos[0] is DummyStrategy


def test_all_strategy_combinations_optuna():
    combinator = PortfolioStrategyCombinator(DummyStrategy)
    trial = MagicMock()
    combos = list(combinator.all_strategy_combinations(optuna_trial=trial))
    assert len(combos) == 1
    # Should be a partial with correct func and keywords
    partial_func = combos[0]
    assert hasattr(partial_func, "func")
    assert partial_func.func is DummyStrategy
    assert partial_func.keywords == {"a": 42}


def test_all_strategy_combinations_optuna_non_dict():
    class DummyStrategy2:
        __name__ = "DummyStrategy2"

        @staticmethod
        def optuna_suggest(trial, prefix=""):
            return DummyStrategy2

    combinator = PortfolioStrategyCombinator(DummyStrategy2)
    trial = MagicMock()
    combos = list(combinator.all_strategy_combinations(optuna_trial=trial))
    assert len(combos) == 1
    # Should be a lambda returning DummyStrategy2
    assert callable(combos[0])
    assert combos[0]() is DummyStrategy2


def test_all_strategy_combinations_error_logged():
    class BadStrategy:
        __name__ = "BadStrategy"

        @staticmethod
        def optuna_suggest(trial, prefix=""):
            raise Exception("fail")

    combinator = PortfolioStrategyCombinator(BadStrategy)
    trial = MagicMock()
    logger = MagicMock()
    combos = list(
        combinator.all_strategy_combinations(optuna_trial=trial, logger=logger)
    )
    assert combos == []
    logger.error.assert_called()


def test_get_strategy_classes_classmethod():
    class MyCombinator(PortfolioStrategyCombinator):
        portfolio_strategy_classes = [DummyStrategy]

    assert MyCombinator.get_strategy_classes() == [DummyStrategy]

    class EmptyCombinator(PortfolioStrategyCombinator):
        portfolio_strategy_classes = []

    assert EmptyCombinator.get_strategy_classes() == []
