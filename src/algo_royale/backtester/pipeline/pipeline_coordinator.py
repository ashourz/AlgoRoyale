import asyncio
from datetime import timedelta
import datetime
from logging import Logger

from algo_royale.backtester.stage_coordinator.backtest_stage_coordinator import (
    BacktestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)


class PipelineCoordinator:
    def __init__(
        self,
        data_ingest_stage_coordinator: DataIngestStageCoordinator,
        feature_engineering_stage_coordinator: FeatureEngineeringStageCoordinator,
        backtest_stage_coordinator: BacktestStageCoordinator,
        logger: Logger,
    ):
        self.logger = logger
        self.data_ingest_stage_coordinator = data_ingest_stage_coordinator
        self.feature_engineering_stage_coordinator = (
            feature_engineering_stage_coordinator
        )
        self.backtest_stage_coordinator = backtest_stage_coordinator

    async def run_async(self, config=None):
        try:
            self.logger.info("Starting Backtest Pipeline...")
            # Data Ingest Stage
            self.logger.info("Running data ingest stage...")
            ingest_success = await self.data_ingest_stage_coordinator.run( 
                start_date= , 
                end_date= 
            )
            if not ingest_success:
                self.logger.error("Data ingest stage failed")
                return False

            # Feature Engineering Stage
            self.logger.info("Running feature engineering stage...")
            fe_success = await self.feature_engineering_stage_coordinator.run(
                load_in_reverse=True
            )
            if not fe_success:
                self.logger.error("Feature engineering stage failed")
                return False

            # Backtest Stage
            self.logger.info("Running backtest stage...")
            backtest_success = await self.backtest_stage_coordinator.run()
            if not backtest_success:
                self.logger.error("Backtest stage failed")
                return False

            self.logger.info("Backtest Pipeline completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False

    
    async def run_walk_forward(self, years_back: int = 5, test_window_years: int = 1):
        today = datetime.today()
        for symbol in self.data_ingest_stage_coordinator.watchlist: ## TODO: get watchlist from config
            self.logger.info(f"Running walk-forward for {symbol}...")
            # Calculate the earliest date for walk-forward
            first_date = today - timedelta(days=365 * years_back)
            last_date = today - timedelta(days=365 * test_window_years)
            # Walk forward in yearly steps
            while first_date < last_date:
                train_start = first_date
                train_end = train_start + timedelta(days=365 * years_back)
                test_start = train_end
                test_end = test_start + timedelta(days=365 * test_window_years)
                if test_end > today:
                    test_end = today

                self.logger.info(
                    f"Walk-forward: {symbol} | Train: {train_start.date()} to {train_end.date()} | Test: {test_start.date()} to {test_end.date()}"
                )

                # Data ingest for train window
                self.logger.info(
                    f"Running data ingest for train window: {train_start.date()} to {train_end.date()}"
                )
                ingest_success = await self.data_ingest_stage_coordinator.run(
                    start_date=train_start, end_date=train_end
                )
                if not ingest_success:
                    self.logger.error("Data ingest stage failed")
                    break
                # Feature engineering for train window
                self.logger.info(
                    f"Running feature engineering for train window: {train_start.date()} to {train_end.date()}"
                )
                fe_success = await self.feature_engineering_stage_coordinator.run(load_in_reverse=True)
                if not fe_success:
                    self.logger.error("Feature engineering stage failed")
                    break
                # Backtest/optimize on train window
                self.logger.info(
                    f"Running backtest/optimization for train window: {train_start.date()} to {train_end.date()}"
                )
                backtest_success = await self.backtest_stage_coordinator.run()
                if not backtest_success:
                    self.logger.error("Backtest stage failed")
                    break
                # Data ingest for test window
                await self.data_ingest_stage_coordinator.run(
                    start_date=test_start, end_date=test_end
                )
                # Feature engineering for test window
                await self.feature_engineering_stage_coordinator.run(load_in_reverse=True)
                # Backtest on test window using best params from train_results
                await self.backtest_stage_coordinator.run(
                    params=train_results["best_params"]
                )
                # Move window forward
                first_date += timedelta(days=365 * test_window_years)
        self.logger.info("Walk-forward completed successfully")
        
        
    def run(self):
        return asyncio.run(self.run_async())
