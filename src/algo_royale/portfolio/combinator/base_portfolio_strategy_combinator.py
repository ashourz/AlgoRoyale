from functools import partial
from typing import Type

from algo_royale.backtester.strategy_combinator.base_strategy_combinator import (
    BaseStrategyCombinator,
)
from algo_royale.portfolio.strategies.base_portfolio_strategy import (
    BasePortfolioStrategy,
)


class PortfolioStrategyCombinator(BaseStrategyCombinator):
    """Base class to generate all combinations of portfolio strategy classes and their parameterizations.
    Subclass and set the class attribute `portfolio_strategy_classes` to a list of strategy classes.
    This class is primarily for compatibility with the base class.
    """

    def __init__(self, strategy_class: Type[BasePortfolioStrategy]):
        """
        Initialize the combinator with a specific portfolio strategy class.
        This is primarily for compatibility with the base class.
        """
        self.strategy_class = strategy_class

    def all_strategy_combinations(
        self,
        optuna_trial=None,
        logger=None,
    ):
        """
        Generate all possible portfolio strategy combinations (with parameterizations if optuna_trial is provided)
        for the single strategy class provided in __init__.
        If optuna_trial is None, yields strategies with default parameters.
        If optuna_trial is provided, uses the strategy's optuna_suggest to generate parameterized strategies.
        """
        strat_cls = self.strategy_class
        try:
            if optuna_trial is not None:
                params = strat_cls.optuna_suggest(
                    optuna_trial, prefix=f"{strat_cls.__name__}_"
                )
                if isinstance(params, dict):
                    yield partial(strat_cls, **params)
                else:
                    yield lambda: params
            else:
                yield strat_cls
        except Exception as e:
            if logger:
                logger.error(f"Error creating portfolio strategy {strat_cls}: {e}")

    @classmethod
    def get_strategy_classes(cls):
        """Return the portfolio strategy classes for this combinator class."""
        return cls.portfolio_strategy_classes or []
