import asyncio
import inspect
import time
from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from typing import Any, Callable, Dict, Type

import optuna
import pandas as pd


class SignalStrategyOptimizer(ABC):
    """
    Abstract base class for signal strategy optimizers.
    This class defines the interface for optimizing signal strategies using Optuna.
    """

    @abstractmethod
    def optimize(
        self,
        symbol: str,
        df: pd.DataFrame,
        window_start_time: datetime,
        window_end_time: datetime,
        n_trials: int = 50,
    ) -> Dict[str, Any]:
        """
        Run the optimization process for a given symbol and DataFrame.
        :param symbol: The symbol to optimize for.
        :param df: DataFrame containing the data for the symbol.
        :param n_trials: Number of trials to run.
        :return: A dictionary with the optimization results.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class SignalStrategyOptimizerImpl(SignalStrategyOptimizer):
    def __init__(
        self,
        strategy_class: Type,
        condition_types: Dict[str, list],
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        logger: Logger,
        metric_name: str = "total_return",
        direction: str = "maximize",
    ):
        """
        :param strategy_class: The strategy class to instantiate.
        :param condition_types: Dict with keys like "entry", "trend", "exit", "stateful_logic"
                                Each value is a list of condition classes with optuna_suggest methods.
        :param backtest_fn: Callable that runs a strategy and returns a result with metrics.
        :param logger: Optional logger for debugging.
        :param metric_name: What metric to optimize.
        :param direction: 'maximize' or 'minimize'.
        """
        self.strategy_class = strategy_class
        self.condition_types = condition_types
        self.backtest_fn = backtest_fn
        self.metric_name = metric_name
        self.direction = direction
        self.logger = logger

    def optimize(
        self,
        symbol: str,
        df: pd.DataFrame,
        window_start_time: datetime,
        window_end_time: datetime,
        n_trials: int = 1,
    ) -> Dict[str, Any]:
        """
        Run the optimization process for a given symbol and DataFrame.
        :param symbol: The symbol to optimize for.
        :param df: DataFrame containing the data for the symbol.
        :param n_trials: Number of trials to run.
            - Default is 50, but can be adjusted based on the complexity of the strategy.
            - 50: A good starting point for most strategies.
            - 100: For more complex strategies or when more precision is needed.
            - 200: For very complex strategies or when the search space is large.
            - 500: For exhaustive searches, but may take a long time.
        :return: A dictionary with the optimization results.
        """
        self.logger.info(
            f"Starting optimization for {symbol} with {self.strategy_class.__name__}"
        )
        self.logger.debug(f"DataFrame lines: {len(df)}")
        study = optuna.create_study(direction=self.direction)
        start_time = time.time()

        def objective(trial, logger=self.logger):
            entry_conds = [
                cond_cls.optuna_suggest(
                    trial, prefix=f"{symbol}_entry_{cond_cls.__name__}_"
                )
                for i, cond_cls in enumerate(self.condition_types.get("entry", []))
            ]
            trend_conds = [
                cond_cls.optuna_suggest(
                    trial, prefix=f"{symbol}_trend_{cond_cls.__name__}_"
                )
                for i, cond_cls in enumerate(self.condition_types.get("trend", []))
            ]
            exit_conds = [
                cond_cls.optuna_suggest(
                    trial, prefix=f"{symbol}_exit_{cond_cls.__name__}_"
                )
                for i, cond_cls in enumerate(self.condition_types.get("exit", []))
            ]
            filter_conds = [
                cond_cls.optuna_suggest(
                    trial, prefix=f"{symbol}_filter_{cond_cls.__name__}_"
                )
                for i, cond_cls in enumerate(self.condition_types.get("filter", []))
            ]
            state_logic = self.condition_types.get("stateful_logic")
            if state_logic:
                state_logic = state_logic.optuna_suggest(
                    trial, prefix=f"{symbol}_logic_{state_logic.__name__}_"
                )

            # Build full candidate kwargs
            init_kwargs = {
                "entry_conditions": entry_conds,
                "trend_conditions": trend_conds,
                "exit_conditions": exit_conds,
                "filter_conditions": filter_conds,
                "stateful_logic": state_logic,
            }

            # Only keep those that the strategy class actually accepts
            valid_params = set(
                inspect.signature(self.strategy_class.__init__).parameters
            )
            strategy_kwargs = {
                k: v for k, v in init_kwargs.items() if k in valid_params
            }

            strategy = self.strategy_class(**strategy_kwargs)
            logger.debug(
                f"[{symbol}] Strategy class: {self.strategy_class.__name__} | Params: {strategy_kwargs}"
            )
            # coro = self.run_async(self.backtest_fn(strategy, df))
            result = self.run_async(self.backtest_fn(strategy, df))
            logger.debug(
                f"[{symbol}] Strategy params: {strategy_kwargs} | Backtest result: {result}"
            )
            try:
                score = result[self.metric_name]
            except Exception as e:
                logger.error(
                    f"[{symbol}] Error extracting metric '{self.metric_name}' from backtest result: {e} | Result: {result}"
                )
                return float("-inf") if self.direction == "maximize" else float("inf")

            # Validate the result dictionary
            if not isinstance(result, dict):
                logger.error(
                    f"[{symbol}] Backtest result is not a dictionary: {result}"
                )
                return float("-inf") if self.direction == "maximize" else float("inf")

            required_metrics = [
                "total_return",
                "sharpe_ratio",
                "win_rate",
                "max_drawdown",
            ]
            missing_metrics = [m for m in required_metrics if m not in result]
            if missing_metrics:
                logger.error(
                    f"[{symbol}] Missing required metrics {missing_metrics} in backtest result: {result}"
                )
                return float("-inf") if self.direction == "maximize" else float("inf")

            # Store the full result in the trial for later retrieval
            trial.set_user_attr("full_result", result)
            if logger:
                logger.debug(f"[{symbol}] Trial result: {score}")
            return score

        study.optimize(objective, n_trials=n_trials)

        duration = round(time.time() - start_time, 2)
        self.logger.info(
            f"Optimization completed for {symbol} in {duration} seconds over {n_trials} trials"
        )
        results = {
            "strategy": self.strategy_class.__name__,
            "best_value": study.best_value,
            "best_params": self._strip_prefixes(study.best_params),
            "meta": {
                "run_time_sec": duration,
                "n_trials": n_trials,
                "symbol": symbol,
                "direction": self.direction,
            },
            "metrics": study.best_trial.user_attrs.get("full_result"),
            "window": {
                "start_date": window_start_time.strftime("%Y-%m-%d"),
                "end_date": window_end_time.strftime("%Y-%m-%d"),
                "window_id": f"{window_start_time.strftime('%Y%m%d')}_{window_end_time.strftime('%Y%m%d')}",
            },
        }
        self.logger.debug(f"Optimization results: {results}")
        return results

    def _strip_prefixes(self, params: dict) -> dict:
        grouped = {
            "entry_conditions": {},
            "exit_conditions": {},
            "filter_conditions": {},
            "trend_conditions": {},
            "logic": {},
        }

        for k, v in params.items():
            # Example: 'GOOG_entry_BollingerBandsEntryCondition_close_col'
            parts = k.split("_")
            if len(parts) >= 4:
                _, cond_type, cond_class = parts[:3]
                param = "_".join(parts[3:])
                conds_key = (
                    f"{cond_type}_conditions" if cond_type != "logic" else "logic"
                )
                if cond_class not in grouped[conds_key]:
                    grouped[conds_key][cond_class] = {}
                grouped[conds_key][cond_class][param] = v
            else:
                grouped[k] = v

        # Convert dicts to lists of dicts for each condition type
        for key in [
            "entry_conditions",
            "exit_conditions",
            "filter_conditions",
            "trend_conditions",
        ]:
            grouped[key] = [
                {cond_class: params} for cond_class, params in grouped[key].items()
            ]

        # For logic, you may want a single dict or object, not a list
        if grouped["logic"]:
            grouped["stateful_logic"] = grouped["logic"]
        grouped.pop("logic", None)

        # Remove empty lists for unused types
        return {k: v for k, v in grouped.items() if v}

    def run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If we're in an event loop, run in a new thread
            import threading

            result_container = {}

            def runner():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                result_container["result"] = new_loop.run_until_complete(coro)
                new_loop.close()

            t = threading.Thread(target=runner)
            t.start()
            t.join()
            return result_container["result"]
        else:
            return asyncio.run(coro)


class MockSignalStrategyOptimizer(SignalStrategyOptimizer):
    """
    Mock version of SignalStrategyOptimizer for testing purposes.
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

    def optimize(
        self,
        symbol: str,
        df: pd.DataFrame,
        window_start_time: datetime,
        window_end_time: datetime,
        n_trials: int = 1,
    ) -> Dict[str, Any]:
        """
        Mock implementation of the optimize method.
        Returns a fixed result for testing purposes.
        """
        if self.mock_results is None:
            raise ValueError("Mock results not set. Call setOptimizeResults() first.")
        return self.mock_results


def mockSignalStrategyOptimizer() -> MockSignalStrategyOptimizer:
    """
    Mock version of SignalStrategyOptimizer for testing purposes.
    """
    return MockSignalStrategyOptimizer()
