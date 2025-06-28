from functools import partial
from typing import Callable, Generator, Type

from algo_royale.backtester.strategy_combinator.base_strategy_combinator import (
    BaseStrategyCombinator,
)
from algo_royale.portfolio.strategies.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class PortfolioStrategyCombinator(BaseStrategyCombinator):
    """
    Base class to generate all combinations of portfolio strategy classes.
    Subclass and set the class attribute `strategy_class` to a strategy class.
    """

    # Single portfolio strategy class to enumerate
    strategy_class: Type[BasePortfolioStrategy] = None

    @classmethod
    def all_strategy_combinations(
        cls,
        optuna_trial=None,
        logger=None,
    ) -> Generator[Callable[[], BasePortfolioStrategy], None, None]:
        """
        Yield a callable that instantiates the single strategy, optionally with optuna params.
        """
        if cls.strategy_class is None:
            if logger:
                logger.error(f"{cls.__name__} has no strategy_class attribute set.")
            return

        if optuna_trial is not None and hasattr(cls.strategy_class, "optuna_suggest"):
            try:
                params = cls.strategy_class.optuna_suggest(optuna_trial)
                if isinstance(params, dict):
                    yield partial(cls.strategy_class, **params)
                else:
                    # If optuna_suggest returns a class or callable, yield a lambda
                    yield lambda: params
            except Exception as e:
                if logger:
                    logger.error(
                        f"Error creating portfolio strategy {cls.strategy_class}: {e}"
                    )
        else:
            yield cls.strategy_class

    @classmethod
    def get_strategy_classes(cls):
        """Return the portfolio strategy classes for this combinator class."""
        if cls.strategy_class is None:
            return []
        return [cls.strategy_class]
