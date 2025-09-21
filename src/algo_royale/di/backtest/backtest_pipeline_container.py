from dependency_injector import containers, providers

from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.di.adapter.adapter_container import AdapterContainer
from algo_royale.di.backtest.data_prep_coordinator_container import (
    DataPrepCoordinatorContainer,
)
from algo_royale.di.backtest.portfolio_backtest_container import (
    PortfolioBacktestContainer,
)
from algo_royale.di.backtest.signal_backtest_container import SignalBacktestContainer
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.repo_container import RepoContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.logging.logger_type import LoggerType


class BacktestPipelineContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    stage_data_container: StageDataContainer = providers.DependenciesContainer()
    feature_engineering_container: FeatureEngineeringContainer = (
        providers.DependenciesContainer()
    )
    factory_container: FactoryContainer = providers.DependenciesContainer()
    adapter_container: AdapterContainer = providers.DependenciesContainer()
    repo_container: RepoContainer = providers.DependenciesContainer()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    data_prep_coordinator_container = providers.Container(
        DataPrepCoordinatorContainer,
        config=config,
        logger_container=logger_container,
        stage_data_container=stage_data_container,
        feature_engineering_container=feature_engineering_container,
        adapter_container=adapter_container,
        repo_container=repo_container,
    )

    signal_backtest_container = providers.Container(
        SignalBacktestContainer,
        config=config,
        data_prep_coordinator_container=data_prep_coordinator_container,
        stage_data_container=stage_data_container,
        factory_container=factory_container,
        logger_container=logger_container,
    )

    portfolio_backtest_container = providers.Container(
        PortfolioBacktestContainer,
        config=config,
        data_prep_coordinator_container=data_prep_coordinator_container,
        stage_data_container=stage_data_container,
        signal_backtest_container=signal_backtest_container,
        factory_container=factory_container,
        logger_container=logger_container,
    )

    pipeline_coordinator = providers.Singleton(
        PipelineCoordinator,
        signal_strategy_walk_forward_coordinator=signal_backtest_container.signal_strategy_walk_forward_coordinator,
        portfolio_walk_forward_coordinator=portfolio_backtest_container.portfolio_walk_forward_coordinator,
        signal_strategy_evaluation_coordinator=signal_backtest_container.strategy_evaluation_coordinator,
        symbol_evaluation_coordinator=signal_backtest_container.symbol_evaluation_coordinator,
        portfolio_evaluation_coordinator=portfolio_backtest_container.portfolio_evaluation_coordinator,
        logger=providers.Factory(
            logger_container.logger, logger_type=LoggerType.PIPELINE_COORDINATOR
        ),
    )
