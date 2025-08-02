import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Mapping, Optional

from algo_royale.backtester.enums.backtest_stage import BacktestStage
from algo_royale.backtester.evaluator.backtest.base_backtest_evaluator import (
    BacktestEvaluator,
)
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.logging.loggable import Loggable


class BaseTestingStageCoordinator(StageCoordinator):
    """
    Base class for strategy testing stage coordinators.
    This class orchestrates the testing stage by loading, processing,
    and writing data for a given backtest stage.
    It handles the execution of strategies and evaluation of results.
    Parameters:
        data_loader (SymbolStrategyDataLoader): Loader for stage data.
        stage_data_manager (StageDataManager): Manager for stage data directories.
        stage (BacktestStage): The stage of the backtest pipeline.
        logger (Logger): Logger for logging information and errors.
        evaluator (BacktestEvaluator): Evaluator for assessing backtest results.
        optimization_root (str): Root directory for saving optimization results.
        optimization_json_filename (str): Name of the JSON file to save optimization results.
    """

    def __init__(
        self,
        data_loader: SymbolStrategyDataLoader,
        stage_data_manager: StageDataManager,
        stage: BacktestStage,
        logger: Loggable,
        evaluator: BacktestEvaluator,
        optimization_root: str,
        optimization_json_filename: str,
    ):
        """Coordinator for the backtest stage."""
        super().__init__()
        self.stage = stage
        self.data_loader = data_loader
        self.stage_data_manager = stage_data_manager
        self.evaluator = evaluator
        self.logger = logger
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
        self.train_window_id = self.stage_data_manager.get_window_id(
            start_date=self.train_start_date, end_date=self.train_end_date
        )

        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.test_window_id = self.stage_data_manager.get_window_id(
            start_date=self.test_start_date, end_date=self.test_end_date
        )
        self.logger.info(
            f"Running {self.stage} for train window {self.train_window_id} | test window {self.test_window_id}"
        )

        if not self.stage.input_stage:
            """ If no incoming stage is defined, skip loading data """
            self.logger.error(f"Stage {self.stage} has no incoming stage defined.")
            raise ValueError(
                f"Stage {self.stage} has no incoming stage defined. Cannot proceed with data loading."
            )

        # Load data for the given stage and date range
        self.logger.info(f"stage:{self.stage} starting data loading.")
        data = await self.data_loader.load_data(
            stage=self.stage.input_stage,
            start_date=self.test_start_date,
            end_date=self.test_end_date,
            reverse_pages=True,
        )
        if not data:
            self.logger.error(f"No data loaded from stage:{self.stage.input_stage}")
            return False

        # Process the data
        self.logger.info(f"stage:{self.stage} starting data processing.")
        processed_data = await self._process_and_write(data)

        if not processed_data:
            self.logger.error(f"Processing failed for stage:{self.stage}")
            return False

        self.logger.info(f"stage:{self.stage} completed and files saved.")
        return True

    def _get_optimization_results(
        self, strategy_name: str, symbol: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, dict]:
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

    def _deep_merge(self, d1, d2):
        merged = dict(d1)  # Copy of d1
        for key, value in d2.items():
            if (
                key in merged
                and isinstance(merged[key], Mapping)
                and isinstance(value, Mapping)
            ):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged
