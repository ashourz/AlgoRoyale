from abc import ABC
from logging import Logger
from typing import Any, Callable, List, Type, Union

import pandas as pd

from algo_royale.backtester.optimizer.portfolio.optimization_direction import (
    OptimizationDirection,
)
from algo_royale.backtester.optimizer.portfolio.portfolio_metric import PortfolioMetric
from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer import (
    MockPortfolioStrategyOptimizer,
    PortfolioStrategyOptimizer,
    PortfolioStrategyOptimizerImpl,
)


class PortfolioStrategyOptimizerFactory(ABC):
    """
    Abstract factory class to create instances of PortfolioStrategyOptimizer.
    This is used to create mock optimizers for testing purposes.
    """

    def create(
        self,
        strategy_class: Type,
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        metric_name: Union[
            PortfolioMetric, List[PortfolioMetric]
        ] = PortfolioMetric.TOTAL_RETURN,
        direction: Union[
            OptimizationDirection, List[OptimizationDirection]
        ] = OptimizationDirection.MAXIMIZE,
    ) -> PortfolioStrategyOptimizer:
        """
        Create a portfolio strategy optimizer instance.
        :param strategy_class: The strategy class to optimize.
        :param backtest_fn: Function to backtest the strategy.
        :param metric_name: Name of the metric to optimize.
        :param direction: Direction of optimization (maximize/minimize).
        :return: PortfolioStrategyOptimizer instance.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class PortfolioStrategyOptimizerFactoryImpl(PortfolioStrategyOptimizerFactory):
    """
    Factory class to create instances of PortfolioStrategyOptimizer.
    This is used to create mock optimizers for testing purposes.
    """

    def __init__(self, logger: Logger):
        """
        Initialize the factory with a logger.
        :param logger: Logger instance for logging.
        """
        self.logger = logger

    def create(
        self,
        strategy_class: Type,
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        metric_name: Union[
            PortfolioMetric, List[PortfolioMetric]
        ] = PortfolioMetric.TOTAL_RETURN,
        direction: Union[
            OptimizationDirection, List[OptimizationDirection]
        ] = OptimizationDirection.MAXIMIZE,
    ) -> PortfolioStrategyOptimizer:
        """
        Create a mock optimizer instance.
        :param strategy_class: The strategy class to optimize.
        :param backtest_fn: Function to backtest the strategy.
        :param logger: Logger instance for logging.
        :param metric_name: Name of the metric to optimize.
        :param direction: Direction of optimization (maximize/minimize).
        :return: MockPortfolioStrategyOptimizerImpl instance.
        """
        return PortfolioStrategyOptimizerImpl(
            strategy_class=strategy_class,
            backtest_fn=backtest_fn,
            logger=self.logger,
            metric_name=metric_name,
            direction=direction,
        )


class MockPortfolioStrategyOptimizerFactory(PortfolioStrategyOptimizerFactory):
    """
    Mock version of PortfolioStrategyOptimizerFactory for testing purposes.
    This class is used to create a mock optimizer that can be used in tests.
    """

    def __init__(self):
        """
        Initialize the mock optimizer factory with default parameters.
        """
        super().__init__(logger=None)  # Logger is not used in mock, set to None
        self.mock_results = None

    def create(
        self,
        strategy_class: Type,
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        metric_name: Union[
            PortfolioMetric, List[PortfolioMetric]
        ] = PortfolioMetric.TOTAL_RETURN,
        direction: Union[
            OptimizationDirection, List[OptimizationDirection]
        ] = OptimizationDirection.MAXIMIZE,
    ) -> PortfolioStrategyOptimizer:
        """
        Create a mock optimizer instance.
        :return: MockPortfolioStrategyOptimizerImpl instance.
        """
        return MockPortfolioStrategyOptimizer()
