import asyncio
import inspect
import time
from logging import Logger
from typing import Any, Callable, Dict, Type

import optuna
import pandas as pd


class StrategyOptimizer:
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
        self, symbol: str, df: pd.DataFrame, n_trials: int = 50
    ) -> Dict[str, Any]:
        study = optuna.create_study(direction=self.direction)
        start_time = time.time()

        def objective(trial, logger=self.logger):
            entry_conds = [
                cond_cls.optuna_suggest(trial, prefix=f"{symbol}_entry_{i}_")
                for i, cond_cls in enumerate(self.condition_types.get("entry", []))
            ]
            trend_conds = [
                cond_cls.optuna_suggest(trial, prefix=f"{symbol}_trend_{i}_")
                for i, cond_cls in enumerate(self.condition_types.get("trend", []))
            ]
            exit_conds = [
                cond_cls.optuna_suggest(trial, prefix=f"{symbol}_exit_{i}_")
                for i, cond_cls in enumerate(self.condition_types.get("exit", []))
            ]
            filter_conds = [
                cond_cls.optuna_suggest(trial, prefix=f"{symbol}_filter_{i}_")
                for i, cond_cls in enumerate(self.condition_types.get("filter", []))
            ]
            state_logic = self.condition_types.get("stateful_logic")
            if state_logic:
                state_logic = state_logic.optuna_suggest(
                    trial, prefix=f"{symbol}_logic_"
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

            coro = self.backtest_fn(strategy, df)
            result = asyncio.run(coro)
            logger.debug(
                f"[{symbol}] Strategy params: {strategy_kwargs} | Backtest result: {result}"
            )
            try:
                score = result[self.metric_name]
            except KeyError:
                raise KeyError(
                    f"Metric '{self.metric_name}' not found in backtest result. Available metrics: {list(result.keys())}"
                )
            if logger:
                logger.debug(f"[{symbol}] Trial result: {score}")
            return score

        study.optimize(objective, n_trials=n_trials)

        duration = round(time.time() - start_time, 2)

        return {
            "strategy": self.strategy_class.__name__,
            "best_value": study.best_value,
            "best_params": study.best_params,
            "meta": {
                "run_time_sec": duration,
                "n_trials": n_trials,
                "symbol": symbol,
            },
        }
