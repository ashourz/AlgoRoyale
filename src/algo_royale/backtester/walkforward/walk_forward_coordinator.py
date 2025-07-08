import asyncio
import os
from datetime import datetime
from logging import Logger
from typing import TYPE_CHECKING

from matplotlib.dates import relativedelta

from algo_royale.backtester.enum.backtest_stage import BacktestStage
from algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.data_staging.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.optimization.base_optimization_stage_coordinator import (
    BaseOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.base_testing_stage_coordinator import (
    BaseTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader

if TYPE_CHECKING:
    pass


class WalkForwardCoordinator:
    def __init__(
        self,
        stage_data_loader: StageDataLoader,
        data_ingest_stage_coordinator: DataIngestStageCoordinator,
        feature_engineering_stage_coordinator: FeatureEngineeringStageCoordinator,
        optimization_stage_coordinator: BaseOptimizationStageCoordinator,
        testing_stage_coordinator: BaseTestingStageCoordinator,
        logger: Logger,
    ):
        self.stage_data_loader = stage_data_loader
        self.logger = logger
        self.data_ingest_stage_coordinator = data_ingest_stage_coordinator
        self.feature_engineering_stage_coordinator = (
            feature_engineering_stage_coordinator
        )
        self.optimization_stage_coordinator = optimization_stage_coordinator
        self.testing_stage_coordinator = testing_stage_coordinator

    async def run_async(self):
        try:
            self.logger.info("Starting Backtest Pipeline...")
            # Run the pipeline stages in sequence
            await self.run_walk_forward()
            self.logger.info("Backtest Pipeline completed successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False

    def walk_forward_windows(
        self, end_date: datetime, n_trials: int = 5, window_size: int = 1
    ):
        """Generate walk-forward windows for backtesting using relativedelta for robust date arithmetic."""
        windows = []
        # Go back n_trials + window_size years for the initial train window
        train_start = end_date - relativedelta(years=(n_trials + window_size))
        train_start = train_start.replace(month=1, day=1)
        for i in range(n_trials):
            train_end = train_start + relativedelta(years=window_size)
            test_start = train_end
            test_end = test_start + relativedelta(years=window_size)
            windows.append(
                {
                    "train_start": train_start,
                    "train_end": train_end,
                    "test_start": test_start,
                    "test_end": test_end,
                }
            )
            train_start = train_start + relativedelta(years=1)
        return windows

    async def run_walk_forward(
        self,
        end_date: datetime = datetime.now(),
        n_trials: int = 5,
        window_size: int = 1,
    ):
        try:
            if end_date is None:
                end_date = datetime.now()
            # Go back n_trials + 1 years for the initial train window
            for window in self.walk_forward_windows(
                end_date=end_date, n_trials=n_trials, window_size=window_size
            ):
                train_start = window["train_start"]
                train_end = window["train_end"]
                test_start = window["test_start"]
                test_end = window["test_end"]

                # Optionally: log or print the window
                self.logger.info(
                    f"Train {train_start.date()} to {train_end.date()}, "
                    f"Test {test_start.date()} to {test_end.date()}"
                )
                # Run the pipeline for this window
                window_result = await self.run_window(
                    train_start=train_start,
                    train_end=train_end,
                    test_start=test_start,
                    test_end=test_end,
                )
                if not window_result:
                    self.logger.error(
                        f"Walk-forward failed: "
                        f"Train {train_start.date()} to {train_end.date()}, "
                        f"Test {test_start.date()} to {test_end.date()}"
                    )
                    continue  # Skip to the next window
                self.logger.info("Walk-forward completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Walk-forward failed: {e}")
            return False

    async def run_window(self, train_start, train_end, test_start, test_end):
        """Run the pipeline for a single walk-forward window."""
        self.logger.info(
            f"Walk-forward: Train: {train_start.date()} to {train_end.date()} | Test: {test_start.date()} to {test_end.date()}"
        )
        # Data ingest for train window
        self.logger.info(
            f"Running data ingest for train window: {train_start.date()} to {train_end.date()}"
        )
        ingest_success = await self.data_ingest_stage_coordinator.run(
            start_date=train_start, end_date=train_end
        )
        if not ingest_success:
            self.logger.error(
                f"Data ingest stage failed for train window: {train_start.date()} to {train_end.date()}"
            )
            # If ingest fails, skip the rest of the pipeline
            return False
        # Check if data has been ingested for the test window
        if not self.has_ingested_data(train_start, train_end):
            self.logger.error(
                f"Data not ingested for train window: {train_start.date()} to {train_end.date()}"
            )
            return False

        # Feature engineering for train window
        self.logger.info(
            f"Running feature engineering for train window: {train_start.date()} to {train_end.date()}"
        )
        fe_success = await self.feature_engineering_stage_coordinator.run(
            start_date=train_start, end_date=train_end, load_in_reverse=True
        )
        if not fe_success:
            self.logger.error("Feature engineering stage failed")
            return False

        # Optimize on train window
        self.logger.info(
            f"Running optimization for train window: {train_start.date()} to {train_end.date()}"
        )
        optimization_success = await self.optimization_stage_coordinator.run(
            start_date=train_start, end_date=train_end
        )
        if not optimization_success:
            self.logger.error("Optimization stage failed")
            return False

        # Data ingest for test window
        self.logger.info(
            f"Running data ingest for test window: {test_start.date()} to {test_end.date()}"
        )
        ingest_success = await self.data_ingest_stage_coordinator.run(
            start_date=test_start, end_date=test_end
        )
        if not ingest_success:
            self.logger.error(
                f"Data ingest stage failed for test window: {test_start.date()} to {test_end.date()}"
            )
            return False

        # Check if data has been ingested for the test window
        if not self.has_ingested_data(test_start, test_end):
            self.logger.error(
                f"Data not ingested for test window: {test_start.date()} to {test_end.date()}"
            )
            return False

        # Feature engineering for test window
        self.logger.info(
            f"Running feature engineering for test window: {test_start.date()} to {test_end.date()}"
        )
        fe_success = await self.feature_engineering_stage_coordinator.run(
            start_date=test_start, end_date=test_end, load_in_reverse=True
        )
        if not fe_success:
            self.logger.error("Feature engineering stage failed")
            return False

        # Test on test window using best params from train_results
        self.logger.info(
            f"Running backtest for test window: {test_start.date()} to {test_end.date()}"
        )
        testing_results = await self.testing_stage_coordinator.run(
            train_start_date=train_start,
            train_end_date=train_end,
            test_start_date=test_start,
            test_end_date=test_end,
        )
        if not testing_results:
            self.logger.error("Testing stage failed")
            return False

        return True

    def has_ingested_data(self, start_date, end_date):
        """
        Returns True if any symbol has a non-empty data file for the given stage and window.
        """
        for symbol in self.stage_data_loader.get_watchlist():
            data_dir = self.data_ingest_stage_coordinator.stage_data_manager.get_directory_path(
                stage=BacktestStage.DATA_INGEST,
                strategy_name=None,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )
            if os.path.isdir(data_dir):
                for fname in os.listdir(data_dir):
                    # Ignore files like 'something.done.csv' or 'something.error.csv'
                    if fname.endswith(".done.csv") or fname.endswith(".error.csv"):
                        continue
                    fpath = os.path.join(data_dir, fname)
                    if os.path.isfile(fpath) and os.path.getsize(fpath) > 0:
                        return True
        return False

    def run(self):
        return asyncio.run(self.run_async())
