import asyncio
from logging import Logger

from algo_royale.backtester.i_data_injest.market_data_fetcher import MarketDataFetcher
from algo_royale.backtester.iii_feature_engineering.feature_engineering_coordinator import (
    FeatureEngineeringCoordinator,
)
from algo_royale.backtester.iv_backtest.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.pipeline.config_validator import ConfigValidator
from algo_royale.backtester.pipeline.data_manage.pipeline_stage import PipelineStage
from algo_royale.backtester.pipeline.data_manage.stage_data_loader import (
    StageDataLoader,
)
from algo_royale.backtester.pipeline.data_preparer.async_data_preparer import (
    AsyncDataPreparer,
)
from algo_royale.backtester.pipeline.strategy_factory import StrategyFactory


class PipelineCoordinator:
    def __init__(
        self,
        data_fetcher: MarketDataFetcher,
        data_loader: StageDataLoader,
        feature_engineering_coordinator: FeatureEngineeringCoordinator,
        backtest_executor: StrategyBacktestExecutor,
        data_preparer: AsyncDataPreparer,
        logger: Logger,
        config_validator: ConfigValidator,
        strategy_factory: StrategyFactory,
    ):
        self.logger = logger
        self.config_validator = config_validator
        self.strategy_factory = strategy_factory
        self.data_fetcher = data_fetcher
        self.data_loader = data_loader
        self.feature_engineering_coordinator = feature_engineering_coordinator
        self.data_preparer = data_preparer
        self.backtest_executor = backtest_executor

    async def run_async(self, config=None):
        try:
            # Validate and normalize configuration
            self.logger.info("Validating configuration...")
            config = self._validate_config(config)
            if not config:
                self.logger.error("Invalid configuration")
                return False

            # Initialize strategies
            self.logger.info("Initializing strategies...")
            strategies = self._initialize_strategies(config)
            if not strategies:
                self.logger.error("No strategies initialized")
                return False

            # Fetch market data
            self.logger.info("Fetching market data...")
            await self.data_fetcher.fetch_all()

            # Feature engineering
            self.logger.info("Running feature engineering...")
            await self.feature_engineering_coordinator.run()

            # Load data
            self.stage = PipelineStage.FEATURE_ENGINEERING
            self.logger.info(f"Loading {self.stage} data...")
            raw_data = await self._load_data(stage=self.stage)
            if not raw_data:
                self.logger.error(f"No {self.stage} data loaded")
                return False

            # Prepare data for backtesting
            self.logger.info("Preparing data for backtesting...")
            prepared_data = self._prepare_data(config, raw_data)
            if not prepared_data:
                self.logger.error(f"No valid data available for {self.stage}")
                return False

            # Run backtest
            self.logger.info("Starting backtest...")
            backtest_result = await self._run_backtest(strategies, prepared_data)
            if not backtest_result:
                self.logger.error("Backtest failed")
                return False

            await self.backtest_executor.save_results()
            self.logger.info("Backtest Pipeline completed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Backtest failed: {e}")
            return False

    def run(self, config=None):
        return asyncio.run(self.run_async(config=config))

    def _validate_config(self, config: dict) -> dict:
        """Validate and normalize configuration"""
        try:
            config = self.config_validator.validate(config or {})
            return config
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False

    def _initialize_strategies(self, config: dict) -> list:
        """Initialize strategies based on the configuration"""
        try:
            strategies = self.strategy_factory.create_strategies(config)
            return strategies
        except Exception as e:
            self.logger.error(f"Strategy initialization failed: {e}")
            return False

    async def _load_data(self, stage: PipelineStage) -> dict:
        """Load data based on the configuration"""
        try:
            data = await self.data_loader.load_all_stage_data(stage=stage)
            return data
        except Exception as e:
            self.logger.error(f"Data loading failed: {e}")
            return False

    def _prepare_data(self, config: dict, data: dict) -> dict:
        """Prepare data for backtesting"""
        try:
            prepared_data = {}
            for symbol, df_iter_factory in data.items():
                prepared_data[symbol] = (
                    lambda symbol=symbol,
                    df_iter_factory=df_iter_factory: self.data_preparer.normalized_stream(
                        symbol, df_iter_factory, config
                    )
                )
            return prepared_data
        except Exception as e:
            self.logger.error(f"Data preparation failed: {e}")
            return False

    async def _run_backtest(self, strategies: list, prepared_data: dict) -> bool:
        """Run backtest using the prepared data and strategies"""
        try:
            await self.backtest_executor.run_backtest(strategies, prepared_data)
            return True
        except Exception as e:
            self.logger.error(f"Backtest execution failed: {e}")
            return False
