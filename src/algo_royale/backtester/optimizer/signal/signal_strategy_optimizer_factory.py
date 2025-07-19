from abc import ABC
from typing import Any, Callable, Dict, Type

import pandas as pd

from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer import (
    MockSignalStrategyOptimizer,
    SignalStrategyOptimizer,
    SignalStrategyOptimizerImpl,
)
from algo_royale.logging.loggable import Loggable


class SignalStrategyOptimizerFactory(ABC):
    """
    Abstract factory class to create instances of SignalStrategyOptimizerImplFactory.
    This is used to create mock optimizers for testing purposes.
    """

    def create(
        self,
        strategy_class: Type,
        condition_types: Dict[str, list],
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        metric_name: str = "total_return",
        direction: str = "maximize",
    ) -> SignalStrategyOptimizer:
        """
        Create a portfolio strategy optimizer instance.
        :param strategy_class: The strategy class to optimize.
        :param backtest_fn: Function to backtest the strategy.
        :param metric_name: Name of the metric to optimize.
        :param direction: Direction of optimization (maximize/minimize).
        :return: SignalStrategyOptimizer instance.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class SignalStrategyOptimizerFactoryImpl(SignalStrategyOptimizerFactory):
    """
    Factory class to create instances of SignalStrategyOptimizer.
    This is used to create mock optimizers for testing purposes.
    """

    def __init__(self, logger: Loggable):
        """
        Initialize the factory with a logger.
        :param logger: Loggable instance for logging.
        """
        self.logger = logger

    def create(
        self,
        strategy_class: Type,
        condition_types: Dict[str, list],
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        metric_name: str = "total_return",
        direction: str = "maximize",
    ) -> SignalStrategyOptimizer:
        """
        Create a mock optimizer instance.
        :param strategy_class: The strategy class to optimize.
        :param backtest_fn: Function to backtest the strategy.
        :param logger: Loggable instance for logging.
        :param metric_name: Name of the metric to optimize.
        :param direction: Direction of optimization (maximize/minimize).
        :return: SignalStrategyOptimizer instance.
        """
        return SignalStrategyOptimizerImpl(
            strategy_class=strategy_class,
            condition_types=condition_types,
            backtest_fn=backtest_fn,
            logger=self.logger,
            metric_name=metric_name,
            direction=direction,
        )


class MockSignalStrategyOptimizerFactory(SignalStrategyOptimizerFactory):
    """
    Mock version of SignalStrategyOptimizerFactory for testing purposes.
    This class is used to create a mock optimizer that can be used in tests.
    """

    def __init__(self):
        """
        Initialize the mock factory.
        This factory does not require a logger since it is used for testing purposes.
        """
        super().__init__()
        self.created_optimizer = None

    def resetCreatedOptimizers(self):
        """
        Reset the list of created optimizers.
        This is useful for testing to ensure a clean state.
        """
        self.created_optimizer = None
        self.created_optimizer_result = None

    def setCreatedOptimizerResult(self, result: Dict[str, Any]):
        """
        Set the result for the created optimizer.
        This is useful for testing to control the output of the mock optimizer.
        :param result: The result to set for the created optimizer.
        """
        self.created_optimizer_result = result

    def create(
        self,
        strategy_class: Type,
        condition_types: Dict[str, list],
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        metric_name: str = "total_return",
        direction: str = "maximize",
    ) -> SignalStrategyOptimizer:
        """
        Create a mock optimizer instance.
        :return: SignalStrategyOptimizerImpl instance.
        """
        self.created_optimizer = MockSignalStrategyOptimizer()
        self.created_optimizer.setOptimizeResults(self.created_optimizer_result)
        return self.created_optimizer


def mockSignalStrategyOptimizerFactory():
    """
    Mock version of SignalStrategyOptimizerFactory for testing purposes.
    This factory creates a mock optimizer that can be used in tests.
    """
    return MockSignalStrategyOptimizerFactory()
