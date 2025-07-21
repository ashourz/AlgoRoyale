import time
from abc import ABC
from typing import Any, Callable, Dict, List, Type, Union

import optuna
import pandas as pd

from algo_royale.backtester.optimizer.portfolio.optimization_direction import (
    OptimizationDirection,
)
from algo_royale.backtester.optimizer.portfolio.portfolio_metric import PortfolioMetric
from algo_royale.logging.loggable import Loggable


class PortfolioStrategyOptimizer(ABC):
    """
    Base class for portfolio strategy optimizers.
    This class is intended to be subclassed and should not be instantiated directly.
    """

    async def optimize(
        self,
        symbols: List[str],
        df: pd.DataFrame,
        n_trials: int = 1,
    ) -> Dict[str, Any]:
        """
        Run the optimization process for a portfolio (all symbols at once) and DataFrame.

        Args:
            symbols (List[str]): List of symbols in the portfolio.
            df (pd.DataFrame): Portfolio matrix DataFrame (all symbols).
            window_start_time (datetime): Start of the optimization window.
            window_end_time (datetime): End of the optimization window.
            n_trials (int): Number of optimization trials.

        Returns:
            Dict[str, Any]: Dictionary with the optimization results.
        """
        raise NotImplementedError("This method should be implemented in a subclass.")


class PortfolioStrategyOptimizerImpl(PortfolioStrategyOptimizer):
    def __init__(
        self,
        strategy_class: Type,
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        logger: Loggable,
        metric_name: Union[
            PortfolioMetric, List[PortfolioMetric]
        ] = PortfolioMetric.TOTAL_RETURN,
        direction: Union[
            OptimizationDirection, List[OptimizationDirection]
        ] = OptimizationDirection.MAXIMIZE,
    ):
        """
        Initialize the portfolio strategy optimizer implementation.

        Args:
            strategy_class (Type): The portfolio strategy class to instantiate.
            backtest_fn (Callable): Callable that runs a strategy and returns a result with metrics.
            logger (Loggable): Logger for debugging.
            metric_name (Union[PortfolioMetric, List[PortfolioMetric]]): Enum or list of enums for metrics to optimize.
            direction (Union[OptimizationDirection, List[OptimizationDirection]]): Enum or list of enums for direction(s) ('maximize'/'minimize').
        """
        self.strategy_class = strategy_class
        self.backtest_fn = backtest_fn
        self.metric_name = metric_name
        self.direction = direction
        self.logger = logger

    async def optimize(
        self,
        symbols: List[str],
        df: pd.DataFrame,
        n_trials: int = 1,
    ) -> Dict[str, Any]:
        """
        Run the optimization process for a portfolio (all symbols at once) and DataFrame.

        Args:
            symbols (List[str]): List of symbols in the portfolio.
            df (pd.DataFrame): Portfolio matrix DataFrame (all symbols).
            window_start_time (datetime): Start of the optimization window.
            window_end_time (datetime): End of the optimization window.
            n_trials (int): Number of optimization trials.

        Returns:
            Dict[str, Any]: Dictionary with the optimization results.
        """
        is_multi = isinstance(self.metric_name, (list, tuple))
        # Always use enums for metric names and directions
        if is_multi:
            metric_enums = self.metric_name
            metric_names = [m.value for m in metric_enums]
            directions = (
                [d.value for d in self.direction]
                if isinstance(self.direction, (list, tuple))
                else [self.direction.value] * len(metric_enums)
            )
            self.logger.info(
                f"[PortfolioStrategyOptimizer] Starting multi-objective portfolio optimization for symbols: {symbols} with strategy: {self.strategy_class.__name__}"
            )
            study = optuna.create_study(directions=directions)
        else:
            metric_enum = self.metric_name
            metric_name = metric_enum.value
            self.logger.info(
                f"[PortfolioStrategyOptimizer] Starting portfolio optimization for symbols: {symbols} with strategy: {self.strategy_class.__name__}"
            )
            study = optuna.create_study(direction=self.direction.value)
        self.logger.debug(
            f"[PortfolioStrategyOptimizer] Portfolio matrix rows: {len(df)}"
        )
        start_time = time.time()

        def objective(trial, logger=self.logger):
            params = self.strategy_class.optuna_suggest(trial, prefix=f"{symbols}_")
            if isinstance(params, dict):
                strategy = self.strategy_class(**params)
            else:
                strategy = params
            logger.debug(
                f"[PortfolioStrategyOptimizer] [{symbols}] PortfolioStrategy: {self.strategy_class.__name__} | Params: {params}"
            )
            result = self.backtest_fn(strategy, df)
            if not result:
                logger.error(
                    f"[{symbols}] Backtest returned empty result for params: {params}"
                )
            logger.debug(
                f"[PortfolioStrategyOptimizer] [{symbols}] PortfolioStrategy params: {params} | Backtest result: {result}"
            )
            # Always extract metrics from result['metrics'] if present
            metrics_dict = result.get("metrics", result)
            if is_multi:
                logger.debug(
                    f"[PortfolioStrategyOptimizer] [{symbols}] Extracting metrics {metric_names} from: {metrics_dict}"
                )
            else:
                logger.debug(
                    f"[PortfolioStrategyOptimizer] [{symbols}] Extracting metric '{metric_name}' from: {metrics_dict}"
                )
            try:
                if is_multi:
                    scores = []
                    for m in metric_names:
                        scores.append(metrics_dict[m])
                    score = tuple(scores)
                else:
                    score = metrics_dict[metric_name]
            except Exception as e:
                logger.error(
                    f"[PortfolioStrategyOptimizer] [{symbols}] Error extracting metric(s) '{self.metric_name}' from backtest result: {e} | Result: {result}"
                )
                if is_multi:
                    fail_val = (
                        float("-inf")
                        if all(
                            d == OptimizationDirection.MAXIMIZE.value
                            for d in directions
                        )
                        else float("inf")
                    )
                    score = tuple([fail_val] * len(metric_names))
                else:
                    score = (
                        float("-inf")
                        if self.direction == OptimizationDirection.MAXIMIZE
                        else float("inf")
                    )
                # Ensure result is a dict with the metric key and fallback value
                if is_multi:
                    result = {m: v for m, v in zip(metric_names, score)}
                else:
                    result = {metric_name: score}
            # Always set full_result as a dict of metrics
            trial.set_user_attr(
                "full_result", metrics_dict if isinstance(metrics_dict, dict) else {}
            )
            logger.debug(
                f"[PortfolioStrategyOptimizer] [{symbols}] Trial result: {score}"
            )
            return score

        study.optimize(objective, n_trials=n_trials)

        duration = round(time.time() - start_time, 2)
        self.logger.info(
            f"[PortfolioStrategyOptimizer] Portfolio optimization completed for symbols: {symbols} in {duration} seconds over {n_trials} trials"
        )
        if is_multi:
            best_trials = study.best_trials
            self.logger.debug(
                f"Best trial numbers: {[t.number for t in best_trials]}, values: {[t.values for t in best_trials]}, params: {[t.params for t in best_trials]}, user_attrs: {[t.user_attrs for t in best_trials]}"
            )
            best_values = [t.values for t in best_trials]
            best_params = [t.params for t in best_trials]
            best_metrics = [t.user_attrs.get("full_result") or {} for t in best_trials]
            # If only one trial, still return a list
            if len(best_metrics) == 1 and not isinstance(best_metrics, list):
                best_metrics = [best_metrics]
        else:
            best_trials = [study.best_trial]
            self.logger.debug(
                f"Best trial number: {best_trials[0].number}, value: {best_trials[0].value}, params: {best_trials[0].params}, user_attrs: {best_trials[0].user_attrs}"
            )
            best_values = study.best_value
            best_params = study.best_params
            best_metrics = study.best_trial.user_attrs.get("full_result") or {}
        # Always ensure metrics is a dict or list of dicts
        self.logger.debug(
            f"[PortfolioStrategyOptimizer] Best trial: {best_trials[0].number} | Value: {best_values} | Params: {best_params} | Metrics: {best_metrics}"
        )
        if not isinstance(best_metrics, dict) and not (
            is_multi and isinstance(best_metrics, list)
        ):
            best_metrics = {} if not is_multi else [{}]
        if not best_metrics:
            self.logger.warning(
                f"[PortfolioStrategyOptimizer] [{symbols}] No metrics found in best trial result."
            )
        results = {
            "strategy": self.strategy_class.__name__,
            "best_value": best_values,
            "best_params": best_params,
            "meta": {
                "run_time_sec": duration,
                "n_trials": n_trials,
                "symbols": symbols,
                "direction": self.direction,
                "multi_objective": is_multi,
            },
            "metrics": best_metrics,
        }
        self.logger.debug(
            f"[PortfolioStrategyOptimizer] Portfolio optimization results: {results}"
        )
        return results

    # Removed run_async method, as all execution is now async-aware.


class MockPortfolioStrategyOptimizer(PortfolioStrategyOptimizer):
    """
    Mock version of PortfolioStrategyOptimizer for testing purposes.
    This class is used to create a mock optimizer that can be used in tests.
    """

    def __init__(self):
        """
        Initialize the mock optimizer with default parameters.
        """
        super().__init__()
        self.mock_results = None

    def setOptimizeResults(self, results: Dict[str, Any]) -> None:
        """
        Set the optimization results for the mock optimizer.
        :param results: Dictionary containing the mock optimization results.
        """
        self.mock_results = results

    def resetOptimizeResults(self) -> None:
        """
        Reset the mock optimization results to None.
        This allows for reusing the mock optimizer with different results.
        """
        self.mock_results = None

    async def optimize(
        self,
        symbols: str,
        df: pd.DataFrame,
        n_trials: int = 1,
    ) -> Dict[str, Any]:
        """
        Mock implementation of the optimize method.
        Returns a fixed result for testing purposes.
        """
        if self.mock_results is None:
            raise ValueError("Mock results not set. Call setOptimizeResults() first.")
        return self.mock_results


def mockPortfolioStrategyOptimizer() -> MockPortfolioStrategyOptimizer:
    """
    Mock version of PortfolioStrategyOptimizer for testing purposes.
    """
    return MockPortfolioStrategyOptimizer()
