import asyncio
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
            ingest_success = await self.data_ingest_stage_coordinator.run()
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

    def run(self):
        return asyncio.run(self.run_async())
