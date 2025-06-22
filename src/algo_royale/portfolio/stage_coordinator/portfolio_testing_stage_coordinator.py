import inspect
import json
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Optional, Sequence

import pandas as pd

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.portfolio.backtest.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.portfolio.backtest.portfolio_evaluator import PortfolioEvaluator
from algo_royale.portfolio.optimizer.portfolio_strategy_combinator import (
    PortfolioStrategyCombinator,
)


class PortfolioTestingStageCoordinator(StageCoordinator):
    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        logger: Logger,
        strategy_combinators: Optional[
            Sequence[type[PortfolioStrategyCombinator]]
        ] = None,
        executor: Optional[PortfolioBacktestExecutor] = None,
        evaluator: Optional[PortfolioEvaluator] = None,
    ):
        super().__init__(
            stage=BacktestStage.BACKTEST,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.strategy_combinators = strategy_combinators
        if not self.strategy_combinators:
            raise ValueError("No portfolio strategy combinators provided")
        self.executor = executor or PortfolioBacktestExecutor()
        self.evaluator = evaluator or PortfolioEvaluator()

    async def run(
        self,
        train_start_date: datetime,
        train_end_date: datetime,
        test_start_date: datetime,
        test_end_date: datetime,
    ) -> bool:
        self.train_start_date = train_start_date
        self.train_end_date = train_end_date
        self.train_window_id = (
            f"{train_start_date.strftime('%Y%m%d')}_{train_end_date.strftime('%Y%m%d')}"
        )
        self.logger.info(
            f"Running portfolio backtest for window {self.train_window_id} from {train_start_date} to {train_end_date}"
        )
        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.test_window_id = (
            f"{test_start_date.strftime('%Y%m%d')}_{test_end_date.strftime('%Y%m%d')}"
        )
        self.logger.info(
            f"Running portfolio backtest for test window {self.test_window_id} from {test_start_date} to {test_end_date}"
        )
        return await super().run(start_date=test_start_date, end_date=test_end_date)

    async def process(
        self,
        prepared_data: Optional[
            Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]
        ] = None,
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        results = {}
        initial_balance = 1_000_000.0  # or make this configurable
        transaction_cost = 0.001  # 0.1% per trade, example
        min_lot = 1  # or set to 100 for round lots
        leverage = 1.0  # or set >1 for margin
        slippage = 0.0  # or set to a value for slippage simulation
        for symbol, df_iter_factory in prepared_data.items():
            if symbol not in prepared_data:
                self.logger.warning(f"No prepared data for symbol: {symbol}")
                continue
            dfs = []
            async for df in df_iter_factory():
                dfs.append(df)
            if not dfs:
                self.logger.warning(
                    f"No data for symbol: {symbol} in window {self.train_window_id}"
                )
                continue
            data = pd.concat(dfs)
            for strategy_combinator in self.strategy_combinators:
                for strat_factory in strategy_combinator.all_strategy_combinations():
                    strategy_class = (
                        strat_factory.func
                        if hasattr(strat_factory, "func")
                        else strat_factory
                    )
                    strategy_name = (
                        strategy_class.__name__
                        if hasattr(strategy_class, "__name__")
                        else str(strategy_class)
                    )
                    train_opt_results = self.get_optimization_results(
                        strategy_name,
                        symbol,
                        self.train_start_date,
                        self.train_end_date,
                    )
                    if not train_opt_results:
                        self.logger.warning(
                            f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                        )
                        continue
                    if (
                        self.train_window_id not in train_opt_results
                        or "optimization" not in train_opt_results[self.train_window_id]
                    ):
                        self.logger.warning(
                            f"No optimization result for {symbol} {strategy_name} {self.train_window_id}"
                        )
                        continue
                    best_params = train_opt_results[self.train_window_id][
                        "optimization"
                    ]["best_params"]
                    valid_params = set(
                        inspect.signature(strategy_class.__init__).parameters
                    )
                    filtered_params = {
                        k: v
                        for k, v in best_params.items()
                        if k in valid_params and k != "self"
                    }
                    self.logger.info(f"Filtered params: {filtered_params}")

                    # Instantiate strategy with filtered_params
                    strategy = strategy_class(**filtered_params)
                    # Run backtest with cash constraints, partial fills, transaction cost, min lot, leverage, slippage
                    backtest_results = self.executor.run_backtest(
                        strategy,
                        data,
                        initial_balance=initial_balance,
                        transaction_cost=transaction_cost,
                        min_lot=min_lot,
                        leverage=leverage,
                        slippage=slippage,
                    )
                    # Evaluate metrics
                    metrics = self.evaluator.evaluate(strategy, backtest_results)
                    test_opt_results = self.get_optimization_results(
                        strategy_name, symbol, self.test_start_date, self.test_end_date
                    )
                    if self.test_window_id not in test_opt_results:
                        test_opt_results[self.test_window_id] = {}
                    test_opt_results[self.test_window_id]["test"] = {"metrics": metrics}
                    test_opt_results_path = self.get_optimization_result_path(
                        strategy_name, symbol, self.test_start_date, self.test_end_date
                    )
                    with open(test_opt_results_path, "w") as f:
                        json.dump(test_opt_results, f, indent=2, default=str)
                    results.setdefault(symbol, {})[strategy_name] = {
                        self.test_window_id: metrics
                    }
        return results

    def get_optimization_results(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ) -> Dict:
        json_path = self.get_optimization_result_path(
            strategy_name, symbol, start_date, end_date
        )
        self.logger.debug(
            f"Loading optimization results from {json_path} for {symbol} {strategy_name}"
        )
        if not json_path.exists() or json_path.stat().st_size == 0:
            self.logger.warning(
                f"No optimization result for {symbol} {strategy_name} start_date={start_date}, end_date={end_date} (optimization result file does not exist or is empty)"
            )
            json_path.parent.mkdir(parents=True, exist_ok=True)
            with open(json_path, "w") as f:
                json.dump({}, f)
            return {}
        with open(json_path, "r") as f:
            try:
                opt_results = json.load(f)
            except json.JSONDecodeError:
                self.logger.warning(
                    f"Optimization result file {json_path} is not valid JSON. Returning empty dict."
                )
                return {}
        return opt_results

    def get_optimization_result_path(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ) -> Path:
        out_dir = self.stage_data_manager.get_directory_path(
            BacktestStage.OPTIMIZATION, strategy_name, symbol, start_date, end_date
        )
        json_path = out_dir / "portfolio_optimization_result.json"
        return json_path

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass
