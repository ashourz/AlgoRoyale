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
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.clock_service import ClockService


class ApplicationContainer(containers.DeclarativeContainer):
    environment = providers.Object(LoggerEnv)

    @staticmethod
    def _get_ini_files(environment):
        env = environment.value.lower()
        if env == "prod":
            return ["env_config_prod.ini"], ["env_secrets_prod.ini"]
        elif env == "test":
            return ["env_config_test.ini"], ["env_secrets_test.ini"]
        else:
            raise ValueError(f"Unsupported environment: {environment}")

    config = providers.Configuration(
        ini_files=providers.Callable(
            lambda environment: ApplicationContainer._get_ini_files(environment)[0],
            environment=environment,
        )
    )
    secrets = providers.Configuration(
        ini_files=providers.Callable(
            lambda environment: ApplicationContainer._get_ini_files(environment)[1],
            environment=environment,
        )
    )
    logger_container = providers.Container(
        LoggerContainer,
        environment=environment,
    )

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

    clock_service = providers.Singleton(
        ClockService,
        clock_adapter=adapter_container.clock_adapter,
        logger=logger_container.provides_logger(logger_type=LoggerType.CLOCK_SERVICE),
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
        clock_service=clock_service,
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
