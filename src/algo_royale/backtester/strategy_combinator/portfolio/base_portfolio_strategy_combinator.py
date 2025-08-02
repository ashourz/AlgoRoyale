from functools import partial
from typing import Callable, Generator, Type

from algo_royale.backtester.strategy.portfolio.base_portfolio_strategy import (
    BasePortfolioStrategy,
)
from algo_royale.logging.loggable import Loggable


class PortfolioStrategyCombinator:
    """
    Base class to generate all combinations of portfolio strategy classes.
    Subclass and set the class attribute `strategy_class` to a strategy class.
    """

    def __init__(
        self,
        strategy_class: Type[BasePortfolioStrategy],
        logger: Loggable = None,
        strategy_logger: Loggable = None,
    ):
        self.logger = logger
        self.strategy_logger = strategy_logger
        # Single portfolio strategy class to enumerate
        self.strategy_class: Type[BasePortfolioStrategy] = strategy_class

    def all_strategy_combinations(
        self,
        optuna_trial=None,
    ) -> Generator[Callable[[], BasePortfolioStrategy], None, None]:
        """
        Yield a callable that instantiates the single strategy, optionally with optuna params.
        """
        if self.strategy_class is None:
            if self.logger:
                self.logger.error(
                    f"{self.__class__.__name__} has no strategy_class attribute set."
                )
            return

        if optuna_trial is not None and hasattr(self.strategy_class, "optuna_suggest"):
            try:
                params = self.strategy_class.optuna_suggest(
                    logger=self.strategy_logger, trial=optuna_trial
                )
                if isinstance(params, dict):
                    yield partial(
                        self.strategy_class, logger=self.strategy_logger, **params
                    )
                else:
                    # If optuna_suggest returns a class or callable, yield a lambda
                    yield lambda: params
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"Error creating portfolio strategy {self.strategy_class}: {e}"
                    )
        else:
            yield self.strategy_class
