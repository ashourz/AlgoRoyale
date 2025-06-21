from abc import ABC
from functools import partial
from typing import Callable, Generator, List, Type

from algo_royale.portfolio.strategies.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class PortfolioStrategyCombinator(ABC):
    """
    Base class to generate all combinations of portfolio strategy classes and their parameterizations.
    Subclass and set the class attribute `portfolio_strategy_classes` to a list of strategy classes.
    """

    portfolio_strategy_classes: List[Type[BasePortfolioStrategy]] = []

    @classmethod
    def all_strategy_combinations(
        cls,
        optuna_trial=None,
        logger=None,
    ) -> Generator[Callable[[], BasePortfolioStrategy], None, None]:
        """
        Generate all possible portfolio strategy combinations (with parameterizations if optuna_trial is provided).
        If optuna_trial is None, yields strategies with default parameters.
        If optuna_trial is provided, uses each strategy's optuna_suggest to generate parameterized strategies.
        """
        for strat_cls in cls.portfolio_strategy_classes:
            try:
                if optuna_trial is not None:
                    # Use optuna_suggest to get params
                    params = strat_cls.optuna_suggest(
                        optuna_trial, prefix=f"{strat_cls.__name__}_"
                    )
                    # If optuna_suggest returns a dict, pass as kwargs
                    if isinstance(params, dict):
                        yield partial(strat_cls, **params)
                    else:
                        # If optuna_suggest returns an instance, just yield it
                        yield lambda: params
                else:
                    # No parameterization, just yield default instance
                    yield strat_cls
            except Exception as e:
                if logger:
                    logger.error(f"Error creating portfolio strategy {strat_cls}: {e}")

    @classmethod
    def get_strategy_classes(cls):
        """Return the portfolio strategy classes for this combinator class."""
        return cls.portfolio_strategy_classes or []
