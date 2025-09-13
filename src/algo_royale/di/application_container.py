from dependency_injector import containers, providers

from algo_royale.di.adapter.adapter_container import AdapterContainer
from algo_royale.di.backtest.backtest_pipeline_container import (
    BacktestPipelineContainer,
)
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.repo_container import RepoContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.di.trading.trading_container import TradingContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["config.ini"])
    secrets = providers.Configuration(ini_files=["secrets.ini"])
    logger_container = LoggerContainer()

    repo_container = providers.Container(
        RepoContainer,
        config=config,
        secrets=secrets,
        logger_container=logger_container,
    )

    adapter_container = providers.Container(
        AdapterContainer,
        config=config,
        secrets=secrets,
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

    backtest_pipeline_container = providers.Container(
        BacktestPipelineContainer,
        config=config,
        stage_data_container=stage_data_container,
        feature_engineering_container=feature_engineering_container,
        factory_container=factory_container,
        adapter_container=adapter_container,
        repo_container=repo_container,
        logger_container=logger_container,
    )

    ledger_service_container = providers.Container(
        LedgerServiceContainer,
        config=config,
        adapter_container=adapter_container,
        repo_container=repo_container,
        logger_container=logger_container,
    )

    trading_container = providers.Container(
        TradingContainer,
        config=config,
        adapter_container=adapter_container,
        repo_container=repo_container,
        feature_engineering_container=feature_engineering_container,
        stage_data_container=stage_data_container,
        factory_container=factory_container,
        ledger_service_container=ledger_service_container,
        logger_container=logger_container,
    )


application_container = ApplicationContainer()
