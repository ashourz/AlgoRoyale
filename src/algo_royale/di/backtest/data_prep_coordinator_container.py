from algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.data_staging.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)
from algo_royale.logging.logger_type import LoggerType


# Refactored to a regular class
class DataPrepCoordinatorContainer:
    def __init__(
        self,
        config,
        logger_container,
        stage_data_container,
        feature_engineering_container,
        adapter_container,
        repo_container,
    ):
        self.config = config
        self.logger_container = logger_container
        self.stage_data_container = stage_data_container
        self.feature_engineering_container = feature_engineering_container
        self.adapter_container = adapter_container
        self.repo_container = repo_container

        self.data_ingest_stage_coordinator = DataIngestStageCoordinator(
            data_loader=self.stage_data_container.symbol_strategy_data_loader,
            data_writer=self.stage_data_container.symbol_strategy_data_writer,
            data_manager=self.stage_data_container.stage_data_manager,
            logger=self.logger_container.logger(
                logger_type=LoggerType.BACKTEST_DATA_INGEST
            ),
            quote_adapter=self.adapter_container.quote_adapter,
            watchlist_repo=self.repo_container.watchlist_repo,
        )

        self.feature_engineering_stage_coordinator = FeatureEngineeringStageCoordinator(
            data_loader=self.stage_data_container.symbol_strategy_data_loader,
            data_writer=self.stage_data_container.symbol_strategy_data_writer,
            data_manager=self.stage_data_container.stage_data_manager,
            logger=self.logger_container.logger(
                logger_type=LoggerType.BACKTEST_FEATURE_ENGINEERING
            ),
            feature_engineer=self.feature_engineering_container.backtest_feature_engineer,
        )
