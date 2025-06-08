import time
from typing import Any, Callable, Dict, Type

import optuna
import pandas as pd


class StrategyOptimizer:
    def __init__(
        self,
        strategy_class: Type,
        condition_types: Dict[str, list],
        backtest_fn: Callable[[Any, pd.DataFrame], Any],
        logger=None,
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
        self.logger = logger or print  # fallback to print

    def optimize(
        self, symbol: str, df: pd.DataFrame, n_trials: int = 50
    ) -> Dict[str, Any]:
        study = optuna.create_study(direction=self.direction)
        start_time = time.time()

        def objective(trial):
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

            state_logic = self.condition_types.get("stateful_logic")
            if state_logic:
                state_logic = state_logic.optuna_suggest(
                    trial, prefix=f"{symbol}_logic_"
                )

            strategy = self.strategy_class(
                entry_conditions=entry_conds,
                trend_conditions=trend_conds,
                exit_conditions=exit_conds,
                stateful_logic=state_logic,
            )

            result = self.backtest_fn(strategy, df)
            score = getattr(result, self.metric_name)

            if self.logger:
                self.logger(f"[{symbol}] Trial result: {score}")
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
