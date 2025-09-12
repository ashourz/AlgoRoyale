from dependency_injector import containers, providers

from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.di.adapter_container import AdapterContainer
from algo_royale.di.client_container import ClientContainer
from algo_royale.di.dao_container import DAOContainer
from algo_royale.di.data_prep_coordinator_container import DataPrepCoordinatorContainer
from algo_royale.di.db_container import DBContainer
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.portfolio_backtest_container import PortfolioBacktestContainer
from algo_royale.di.repo_container import RepoContainer
from algo_royale.di.signal_backtest_container import SignalBacktestContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.logging.logger_type import LoggerType


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["config.ini"])
    secrets = providers.Configuration(ini_files=["secrets.ini"])
    logger_container = LoggerContainer()

    db_container = providers.Container(DBContainer, config=config, secrets=secrets)

    dao_container = providers.Container(
        DAOContainer,
        config=config,
        db_container=db_container,
        logger_container=logger_container,
    )

    repo_container = providers.Container(
        RepoContainer,
        config=config,
        dao=dao_container,
        logger_container=logger_container,
    )

    client_container = providers.Container(
        ClientContainer,
        config=config,
        secrets=secrets,
        logger_container=logger_container,
    )

    adapter_container = providers.Container(
        AdapterContainer,
        client_container=client_container,
        logger_container=logger_container,
    )

    stage_data_container = providers.Container(
        StageDataContainer,
        config=config,
        logger_container=logger_container,
        watchlist_repo=repo_container.watchlist_repo,
    )

    factory_container = providers.Container(
        FactoryContainer,
        config=config,
        logger_container=logger_container,
    )

    feature_engineering_container = providers.Container(
        FeatureEngineeringContainer,
        config=config,
        logger_container=logger_container,
    )

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
        logger=logger_container.provides_logger(
            logger_type=LoggerType.PIPELINE_COORDINATOR
        ),
    )


application_container = ApplicationContainer()
