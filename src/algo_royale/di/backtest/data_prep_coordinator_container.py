from dependency_injector import containers, providers

from algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.data_staging.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)
from algo_royale.di.adapter.adapter_container import AdapterContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.repo_container import RepoContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.logging.logger_type import LoggerType


class DataPrepCoordinatorContainer(containers.DeclarativeContainer):
    """Stage Coordinator Container"""

    config = providers.Configuration()
    logger_container: LoggerContainer = providers.DependenciesContainer()
    stage_data_container: StageDataContainer = providers.DependenciesContainer()
    feature_engineering_container: FeatureEngineeringContainer = (
        providers.DependenciesContainer()
    )
    adapter_container: AdapterContainer = providers.DependenciesContainer()
    repo_container: RepoContainer = providers.DependenciesContainer()

    data_ingest_stage_coordinator = providers.Singleton(
        DataIngestStageCoordinator,
        data_loader=stage_data_container.stage_data_loader,
        data_writer=stage_data_container.symbol_strategy_data_writer,
        data_manager=stage_data_container.stage_data_manager,
        logger=logger_container.logger(logger_type=LoggerType.BACKTEST_DATA_INGEST),
        quote_adapter=adapter_container.quote_adapter,
        watchlist_repo=repo_container.watchlist_repo,
    )

    feature_engineering_stage_coordinator = providers.Singleton(
        FeatureEngineeringStageCoordinator,
        data_loader=stage_data_container.symbol_strategy_data_loader,
        data_writer=stage_data_container.symbol_strategy_data_writer,
        data_manager=stage_data_container.stage_data_manager,
        logger=logger_container.logger(
            logger_type=LoggerType.BACKTEST_FEATURE_ENGINEERING
        ),
        feature_engineer=feature_engineering_container.backtest_feature_engineer,
    )
