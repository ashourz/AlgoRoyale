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
    Subclass and set the class attribute `portfolio_strategy_classes` to a list of strategy classes.
    """

    # List of portfolio strategy classes to enumerate
    strategy_class: Type[BasePortfolioStrategy] = None

    @classmethod
    def all_strategy_combinations(
        cls,
        logger=None,
    ) -> Generator[Callable[[], BasePortfolioStrategy], None, None]:
        """
        Yield a callable that instantiates the single strategy.
        """
        if cls.strategy_class is None:
            if logger:
                logger.error(f"{cls.__name__} has no strategy_class attribute set.")
            return

        try:
            yield partial(cls.strategy_class)
        except Exception as e:
            if logger:
                logger.error(
                    f"Error creating portfolio strategy {cls.strategy_class}: {e}"
                )

    @classmethod
    def get_strategy_classes(cls):
        """Return the portfolio strategy classes for this combinator class."""
        return [cls.strategy_class] or []
