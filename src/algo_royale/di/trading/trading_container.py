from algo_royale.di.trading.market_session_container import MarketSessionContainer
from algo_royale.di.trading.order_generator_service_container import (
    OrderGeneratorServiceContainer,
)
from algo_royale.di.trading.registry_container import RegistryContainer
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.trade_orchestrator import TradeOrchestrator


# Refactored to a regular class
class TradingContainer:
    def __init__(
        self,
        config,
        adapter_container,
        repo_container,
        feature_engineering_container,
        stage_data_container,
        factory_container,
        ledger_service_container,
        logger_container,
        clock_service,
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
            premarket_open_duration_minutes=30,
        )
