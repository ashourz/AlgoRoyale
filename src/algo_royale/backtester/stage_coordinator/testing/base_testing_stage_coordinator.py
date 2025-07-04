import json
from datetime import datetime
from logging import Logger
from pathlib import Path
from typing import Dict, Optional, Sequence

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
from algo_royale.backtester.executor.base_backtest_executor import BacktestExecutor
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
from algo_royale.backtester.strategy_combinator.signal.base_signal_strategy_combinator import (
    SignalStrategyCombinator,
)


class BaseTestingStageCoordinator(StageCoordinator):
    """
    Base class for strategy testing stage coordinators.
    Subclasses must implement process().
    """

    def __init__(
        self,
        data_loader: StageDataLoader,
        data_preparer: AsyncDataPreparer,
        data_writer: StageDataWriter,
        stage_data_manager: StageDataManager,
        stage: BacktestStage,
        logger: Logger,
        executor: BacktestExecutor,
        evaluator: BacktestEvaluator,
        strategy_combinators: Sequence[type[SignalStrategyCombinator]],
        optimization_root: str,
        optimization_json_filename: str,
    ):
        """Coordinator for the backtest stage."""
        super().__init__(
            stage=stage,
            data_loader=data_loader,
            data_preparer=data_preparer,
            data_writer=data_writer,
            stage_data_manager=stage_data_manager,
            logger=logger,
        )
        self.strategy_combinators = strategy_combinators
        self.executor = executor
        self.evaluator = evaluator
        self.optimization_root = Path(optimization_root)
        if not self.optimization_root.is_dir():
            ## Create the directory if it does not exist
            self.optimization_root.mkdir(parents=True, exist_ok=True)
        self.optimization_json_filename = optimization_json_filename

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
            f"Running {self.stage} for window {self.train_window_id} from {train_start_date} to {train_end_date}"
        )
        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.test_window_id = (
            f"{test_start_date.strftime('%Y%m%d')}_{test_end_date.strftime('%Y%m%d')}"
        )
        self.logger.info(
            f"Running {self.stage} for test window {self.test_window_id} from {test_start_date} to {test_end_date}"
        )
        return await super().run(start_date=test_start_date, end_date=test_end_date)

    async def _write(self, stage, processed_data):
        # No-op: writing is handled in process()
        pass

    def _get_optimization_results(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ) -> Dict:
        """Get optimization results for a given strategy and symbol."""
        json_path = self._get_optimization_result_path(
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        self.logger.debug(
            f"Loading optimization results from {json_path} for Symbol:{symbol} | Strategy:{strategy_name}"
        )
        if not json_path.exists() or json_path.stat().st_size == 0:
            self.logger.warning(
                f"No optimization result for Symbol:{symbol} | Strategy:{strategy_name} start_date={start_date}, end_date={end_date} (optimization result file does not exist or is empty)"
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

    def _get_optimization_result_path(
        self,
        strategy_name: str,
        symbol: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> Path:
        """Get the path to the optimization result JSON file for a given strategy and symbol."""
        out_dir = self.stage_data_manager.get_directory_path(
            base_dir=self.optimization_root,
            strategy_name=strategy_name,
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / self.optimization_json_filename
