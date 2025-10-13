from unittest.mock import MagicMock

from algo_royale.backtester.strategy_combinator.portfolio.base_portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class DummyStrategy:
    __name__ = "DummyStrategy"

    def __init__(self, a=1):
        self.a = a

    @staticmethod
    def optuna_suggest(logger=None, trial=None, prefix=""):
        return {"a": 42}


class TestPortfolioStrategyCombinator:
    def test_all_strategy_combinations_default(self):
        combos = list(
            PortfolioStrategyCombinator(
                strategy_class=DummyStrategy
            ).all_strategy_combinations()
        )
        assert len(combos) == 1
        assert combos[0] is DummyStrategy

    def test_all_strategy_combinations_optuna(self):
        trial = MagicMock()
        combos = list(
            PortfolioStrategyCombinator(
                strategy_class=DummyStrategy
            ).all_strategy_combinations(optuna_trial=trial)
        )
        assert len(combos) == 1
        # Should be a partial with correct func and keywords
        partial_func = combos[0]
        assert hasattr(partial_func, "func")
        assert partial_func.func is DummyStrategy
        assert partial_func.keywords == {"a": 42, "logger": None}

    def test_all_strategy_combinations_optuna_non_dict(self):
        class DummyStrategy2:
            __name__ = "DummyStrategy2"

            @staticmethod
            def optuna_suggest(trial, prefix=""):
                return DummyStrategy2

        class DummyCombinator(PortfolioStrategyCombinator):
            def __init__(self):
                super().__init__(strategy_class=DummyStrategy2)

        trial = MagicMock()
        combos = list(DummyCombinator().all_strategy_combinations(optuna_trial=trial))
        assert len(combos) == 0

    def test_all_strategy_combinations_error_logged(self):
        class BadStrategy:
            __name__ = "BadStrategy"

            @staticmethod
            def optuna_suggest(trial, prefix=""):
                raise Exception("fail")

        class BadCombinator(PortfolioStrategyCombinator):
            def __init__(self, logger=None, strategy_logger=None):
                super().__init__(
                    strategy_class=BadStrategy,
                    logger=logger,
                    strategy_logger=strategy_logger,
                )

        trial = MagicMock()
        logger = MagicMock()
        combos = list(
            BadCombinator(logger=logger).all_strategy_combinations(optuna_trial=trial)
        )
        assert combos == []
        logger.error.assert_called()

    def test_get_strategy_classes_classmethod(self):
        class MyCombinator(PortfolioStrategyCombinator):
            strategy_class = DummyStrategy

        assert MyCombinator.get_strategy_classes() == [DummyStrategy]

        class EmptyCombinator(PortfolioStrategyCombinator):
            strategy_class = None

        assert EmptyCombinator.get_strategy_classes() == []
