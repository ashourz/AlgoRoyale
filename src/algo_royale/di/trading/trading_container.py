from algo_royale.di.adapter.adapter_container import AdapterContainer
from algo_royale.di.factory_container import FactoryContainer
from algo_royale.di.feature_engineering_container import FeatureEngineeringContainer
from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo.repo_container import RepoContainer
from algo_royale.di.stage_data_container import StageDataContainer
from algo_royale.di.trading.market_session_container import MarketSessionContainer
from algo_royale.di.trading.order_generator_service_container import (
    OrderGeneratorServiceContainer,
)
from algo_royale.di.trading.registry_container import RegistryContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.clock_service import ClockService
from algo_royale.services.trade_orchestrator import TradeOrchestrator


# Refactored to a regular class
class TradingContainer:
    def __init__(
        self,
        config,
        adapter_container: AdapterContainer,
        repo_container: RepoContainer,
        feature_engineering_container: FeatureEngineeringContainer,
        stage_data_container: StageDataContainer,
        factory_container: FactoryContainer,
        ledger_service_container: LedgerServiceContainer,
        logger_container: LoggerContainer,
        clock_service: ClockService,
    ):
        self.config = config
        self.adapter_container = adapter_container
        self.repo_container = repo_container
        self.feature_engineering_container = feature_engineering_container
        self.stage_data_container = stage_data_container
        self.factory_container = factory_container
        self.ledger_service_container = ledger_service_container
        self.logger_container = logger_container
        self.clock_service = clock_service

    @property
    def registry_container(self) -> RegistryContainer:
        return RegistryContainer(
            config=self.config,
            factory_container=self.factory_container,
            stage_data_container=self.stage_data_container,
            ledger_service_container=self.ledger_service_container,
            logger_container=self.logger_container,
        )

    @property
    def order_generator_service_container(self) -> OrderGeneratorServiceContainer:
        return OrderGeneratorServiceContainer(
            config=self.config,
            adapter_container=self.adapter_container,
            repo_container=self.repo_container,
            feature_engineering_container=self.feature_engineering_container,
            ledger_service_container=self.ledger_service_container,
            registry_container=self.registry_container,
            logger_container=self.logger_container,
        )

    @property
    def market_session_container(self) -> MarketSessionContainer:
        return MarketSessionContainer(
            clock_service=self.clock_service,
            logger_container=self.logger_container,
            ledger_service_container=self.ledger_service_container,
            order_generator_service_container=self.order_generator_service_container,
        )

    @property
    def trade_orchestrator(self) -> TradeOrchestrator:
        return TradeOrchestrator(
            clock_service=self.clock_service,
            market_session_service=self.market_session_container.market_session_service,
            logger=self.logger_container.logger(
                logger_type=LoggerType.TRADE_ORCHESTRATOR
            ),
            premarket_open_duration_minutes=int(
                self.config["trading"].get("premarket_open_duration_minutes", 30)
            ),
        )
