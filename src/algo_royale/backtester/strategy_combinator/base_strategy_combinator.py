from abc import ABC, abstractmethod
from typing import Callable, Generator

from algo_royale.backtester.strategy.base_strategy import BaseStrategy


class BaseStrategyCombinator(ABC):
    """Base class to generate all combinations of portfolio strategy classes and their parameterizations.
    Subclass and set
    the class attribute `portfolio_strategy_classes` to a list of strategy classes.
    """

    @abstractmethod
    def all_strategy_combinations(
        cls,
        optuna_trial=None,
        logger=None,
        debug: bool = False,
    ) -> Generator[Callable[[], BaseStrategy], None, None]:
        """
        Generate all possible strategy combinations (with parameterizations if optuna_trial is provided).
        If optuna_trial is None, yields strategies with default parameters.
        If optuna_trial is provided, uses each strategy's optuna_suggest to generate parameterized strategies.
        """
        raise NotImplementedError(
            f"{cls.__name__}.all_strategy_combinations() must be implemented."
        )
