from dependency_injector import containers, providers

from algo_royale.di.adapter_container import AdapterContainer
from algo_royale.di.client_container import ClientContainer
from algo_royale.di.dao_container import DAOContainer
from algo_royale.di.db_container import DBContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo_container import RepoContainer
from algo_royale.di.stage_data_container import StageDataContainer


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

    pipeline_coordinator = providers.Singleton(
        PipelineCoordinator,
        strategy_walk_forward_coordinator=strategy_walk_forward_coordinator,
        portfolio_walk_forward_coordinator=portfolio_walk_forward_coordinator,
        strategy_evaluation_coordinator=strategy_evaluation_coordinator,
        symbol_evaluation_coordinator=symbol_evaluation_coordinator,
        portfolio_evaluation_coordinator=portfolio_evaluation_coordinator,
        logger=logger_backtest_pipeline,
    )


application_container = ApplicationContainer()
