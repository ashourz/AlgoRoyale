import asyncio
from logging import Logger


class PipelineCoordinator:
    def __init__(
        self,
        data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator,
        backtest_stage_coordinator,
        logger: Logger,
        strategy_factory,
    ):
        self.logger = logger
        self.strategy_factory = strategy_factory
        self.data_ingest_stage_coordinator = data_ingest_stage_coordinator
        self.feature_engineering_stage_coordinator = (
            feature_engineering_stage_coordinator
        )
        self.backtest_stage_coordinator = backtest_stage_coordinator

    async def run_async(self, config=None):
        try:
            # Initialize strategies
            self.logger.info("Initializing strategies...")
            strategies = self._initialize_strategies(config)
            if not strategies:
                self.logger.error("No strategies initialized")
                return False

            # Data Ingest Stage
            self.logger.info("Running data ingest stage...")
            ingest_success = await self.data_ingest_stage_coordinator.run()
            if not ingest_success:
                self.logger.error("Data ingest stage failed")
                return False

            # Feature Engineering Stage
            self.logger.info("Running feature engineering stage...")
            fe_success = await self.feature_engineering_stage_coordinator.run()
            if not fe_success:
                self.logger.error("Feature engineering stage failed")
                return False

            # Backtest Stage
            self.logger.info("Running backtest stage...")
            self.backtest_stage_coordinator.strategies = (
                strategies  # Inject strategies if needed
            )
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

    def _initialize_strategies(self, config: dict) -> list:
        """Initialize strategies based on the configuration"""
        try:
            strategies = self.strategy_factory.create_strategies(config)
            return strategies
        except Exception as e:
            self.logger.error(f"Strategy initialization failed: {e}")
            return False
