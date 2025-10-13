from algo_royale.di.ledger_service_container import LedgerServiceContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.trading.order_generator_service_container import (
    OrderGeneratorServiceContainer,
)
from algo_royale.logging.logger_type import LoggerType
from algo_royale.services.clock_service import ClockService
from algo_royale.services.market_session_service import MarketSessionService
from algo_royale.services.order_monitor_service import OrderMonitorService
from algo_royale.services.orders_execution_service import OrderExecutionService


class MarketSessionContainer:
    def __init__(
        self,
        clock_service: ClockService,
        logger_container: LoggerContainer,
        ledger_service_container: LedgerServiceContainer,
        order_generator_service_container: OrderGeneratorServiceContainer,
    ):
        self.clock_service = clock_service
        self.logger_container = logger_container
        self.ledger_service_container = ledger_service_container
        self.order_generator_service_container = order_generator_service_container

    @property
    def order_execution_service(self) -> OrderExecutionService:
        return OrderExecutionService(
            ledger_service=self.ledger_service_container.ledger_service,
            symbol_hold_service=self.order_generator_service_container.symbol_hold_service,
            order_generator_service=self.order_generator_service_container.order_generator_service,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ORDER_EXECUTION_SERVICE
            ),
        )

    @property
    def order_monitor_service(self) -> OrderMonitorService:
        return OrderMonitorService(
            ledger_service=self.ledger_service_container.ledger_service,
            order_event_service=self.order_generator_service_container.order_event_service,
            trades_service=self.ledger_service_container.trades_service,
            clock_service=self.clock_service,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ORDER_MONITOR_SERVICE
            ),
        )

    @property
    def market_session_service(self) -> MarketSessionService:
        return MarketSessionService(
            order_service=self.ledger_service_container.order_service,
            positions_service=self.ledger_service_container.positions_service,
            symbol_service=self.order_generator_service_container.symbol_service,
            symbol_hold_service=self.order_generator_service_container.symbol_hold_service,
            trade_service=self.ledger_service_container.trades_service,
            ledger_service=self.ledger_service_container.ledger_service,
            order_execution_service=self.order_execution_service,
            order_monitor_service=self.order_monitor_service,
            clock_service=self.clock_service,
            logger=self.logger_container.logger(
                logger_type=LoggerType.MARKET_SESSION_SERVICE
            ),
        )
