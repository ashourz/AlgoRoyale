from dependency_injector import containers, providers

from algo_royale.di.adapter_container import AdapterContainer
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo_container import RepoContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.di.trading.market_session_container import MarketSessionContainer
from algo_royale.di.trading.order_generator_service_container import (
    OrderGeneratorServiceContainer,
)
from algo_royale.di.trading.registry_container import RegistryContainer


class TradingContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    adapter_container: AdapterContainer = providers.DependenciesContainer()
    repo_container: RepoContainer = providers.DependenciesContainer()
    feature_engineering_container: FeatureEngineeringContainer = (
        providers.DependenciesContainer()
    )
    stage_data_container: StageDataContainer = providers.DependenciesContainer()
    factory_container: FactoryContainer = providers.DependenciesContainer()
    ledger_service_container: LedgerServiceContainer = providers.DependenciesContainer()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    registry_container = providers.Container(
        RegistryContainer,
        config=config,
        factory_container=factory_container,
        stage_data_container=stage_data_container,
        ledger_service_container=ledger_service_container,
        logger_container=logger_container,
    )

    test_order_generator_service_container = providers.Container(
        OrderGeneratorServiceContainer,
        adapter_container=adapter_container,
        repo_container=repo_container,
        feature_engineering_container=feature_engineering_container,
        ledger_service_container=ledger_service_container,
        registry_container=registry_container,
        logger_container=logger_container,
        is_live=providers.Object(False),
    )

    live_order_generator_service_container = providers.Container(
        OrderGeneratorServiceContainer,
        adapter_container=adapter_container,
        repo_container=repo_container,
        feature_engineering_container=feature_engineering_container,
        ledger_service_container=ledger_service_container,
        registry_container=registry_container,
        logger_container=logger_container,
        is_live=providers.Object(True),
    )

    test_market_session_container = providers.Container(
        MarketSessionContainer,
        logger_container=logger_container,
        ledger_service_container=ledger_service_container,
        order_generator_service_container=test_order_generator_service_container,
    )

    live_market_session_container = providers.Container(
        MarketSessionContainer,
        logger_container=logger_container,
        ledger_service_container=ledger_service_container,
        order_generator_service_container=live_order_generator_service_container,
    )
