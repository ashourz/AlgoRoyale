import json
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Callable, Dict, Mapping, Optional, Sequence

import pandas as pd

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.stage_coordinator import StageCoordinator
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.strategy_combinator.base_strategy_combinator import (
    BaseStrategyCombinator,
)
from algo_royale.logging.loggable import Loggable


class BaseOptimizationStageCoordinator(StageCoordinator):
    """
    Base class for strategy optimization stage coordinators.
    Subclasses must implement process().
    Parameters:
        stage: BacktestStage enum value indicating the stage of the backtest.
        data_loader: Data loader for the stage.
        stage_data_manager: StageDataManager for managing stage data.
        strategy_combinators: List of strategy combinator classes to use.
        logger: Loggable instance.
    """

    def __init__(
        self,
        stage: BacktestStage,
        data_loader: SymbolStrategyDataLoader,
        stage_data_manager: StageDataManager,
        strategy_combinators: Sequence[type[BaseStrategyCombinator]],
        logger: Loggable,
    ):
        """Coordinator for the backtest stage."""
        super().__init__()
        self.stage = stage
        self.data_loader = data_loader
        self.stage_data_manager = stage_data_manager
        self.strategy_combinators = strategy_combinators
        self.logger = logger

    async def run(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> bool:
        """
        Orchestrate the stage: load, process, write.
        """
        self.start_date = start_date
        self.end_date = end_date
        self.window_id = self.stage_data_manager.get_window_id(
            start_date=self.start_date, end_date=self.end_date
        )

        self.logger.info(
            f"Starting stage: {self.stage} | start_date: {start_date} | end_date: {end_date}"
        )
        if not self.stage.input_stage:
            """ If no incoming stage is defined, skip loading data """
            self.logger.error(f"Stage {self.stage} has no incoming stage defined.")
            raise ValueError(
                f"Stage {self.stage} has no incoming stage defined. Cannot proceed with data loading."
            )

        # Load the data from the input stage
        self.logger.info(f"stage:{self.stage} starting data loading.")
        data = await self._load_input_data(
            start_date=self.start_date,
            end_date=self.end_date,
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

    async def _load_input_data(
        self,
        start_date: datetime,
        end_date: datetime,
        reverse_pages: bool = True,
    ) -> Dict[str, Callable[[], AsyncIterator[pd.DataFrame]]]:
        """
        Load input data for the stage.
        This method should be overridden by subclasses if they need to load specific data.
        """
        self.logger.info(
            f"Loading input data for stage: {self.stage} | start_date: {start_date} | end_date: {end_date}"
        )
        return await self.data_loader.load_data(
            stage=self.stage.input_stage,
            start_date=start_date,
            end_date=end_date,
            reverse_pages=reverse_pages,
        )

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
