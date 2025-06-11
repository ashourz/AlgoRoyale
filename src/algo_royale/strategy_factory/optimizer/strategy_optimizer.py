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
        self,
        symbol: str,
        df: pd.DataFrame,
        n_trials: int = 200,  ## TODO: change back to 50
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

            coro = self.backtest_fn(strategy, df)
            result = asyncio.run(coro)
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
            "best_params": self._strip_prefixes(study.best_params, symbol),
            "meta": {
                "run_time_sec": duration,
                "n_trials": n_trials,
                "symbol": symbol,
                "direction": self.direction,
            },
            "best_result": study.best_trial.user_attrs.get(
                "full_result"
            ),  # <-- add this line
        }
        self.logger.debug(f"Optimization results: {results}")
        return results

    def _strip_prefixes(self, params: dict, symbol: str) -> dict:
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
