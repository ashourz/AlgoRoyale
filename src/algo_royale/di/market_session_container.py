from dependency_injector import containers, providers

from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.order_generator_service_container import (
    OrderGeneratorServiceContainer,
)
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.market_session_service import MarketSessionService
from algo_royale.services.order_monitor_service import OrderMonitorService
from algo_royale.services.orders_execution_service import OrderExecutionService


class MarketSessionContainer(containers.DeclarativeContainer):
    logger_container: LoggerContainer = providers.DependenciesContainer()
    ledger_service_container: LedgerServiceContainer = providers.DependenciesContainer()
    order_generator_service_container: OrderGeneratorServiceContainer = (
        providers.DependenciesContainer()
    )

    order_execution_service = providers.Singleton(
        OrderExecutionService,
        ledger_service=ledger_service_container.ledger_service,
        symbol_hold_service=order_generator_service_container.symbol_hold_service,
        order_generator_service=order_generator_service_container.order_generator_service,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.ORDER_EXECUTION_SERVICE
        ),
    )

    order_monitor_service = providers.Singleton(
        OrderMonitorService,
        ledger_service=ledger_service_container.ledger_service,
        order_event_service=order_generator_service_container.order_event_service,
        trades_service=ledger_service_container.trades_service,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.ORDER_MONITOR_SERVICE
        ),
    )

    market_session_service = providers.Singleton(
        MarketSessionService,
        order_service=ledger_service_container.order_service,
        positions_service=ledger_service_container.positions_service,
        symbol_service=order_generator_service_container.symbol_service,
        symbol_hold_service=order_generator_service_container.symbol_hold_service,
        trade_service=ledger_service_container.trades_service,
        ledger_service=ledger_service_container.ledger_service,
        order_execution_service=order_execution_service,
        order_monitor_service=order_monitor_service,
        logger=logger_container.provides_logger(
            logger_type=LoggerType.MARKET_SESSION_SERVICE
        ),
    )
