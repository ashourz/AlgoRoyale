from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.services.ledger_service import LedgerService
from algo_royale.services.orders_execution_service import OrderExecutionServices


class OrchestratorService:
    def __init__(
        self,
        ledger_service: LedgerService,
        order_execution_service: OrderExecutionServices,
    ):
        self.ledger_service = ledger_service
        self.order_execution_service = order_execution_service

    async def start(self) -> dict[str, AsyncSubscriber] | None:
        """Start the order execution services."""
        try:
            self._init_ledger_service()
            await self._async_start_order_execution()
        except Exception as e:
            self.logger.error(f"Error starting orchestrator service: {e}")
        return None

    async def stop(self) -> None:
        """Stop the order execution services."""
        try:
            await self.order_execution_service.stop()
        except Exception as e:
            self.logger.error(f"Error stopping orchestrator service: {e}")

    def _init_ledger_service(self) -> None:
        """Initialize the ledger service."""
        try:
            available_cash = self.ledger_service.get_available_cash()
            self.ledger_service.init_sod_cash(available_cash)
        except Exception as e:
            self.logger.error(f"Error initializing ledger service: {e}")

    async def _async_start_order_execution(self) -> None:
        """Start the order execution services."""
        try:
            symbols = await self.symbol_service.async_get_symbols()
            self.order_execution_service.start(symbols)
        except Exception as e:
            self.logger.error(f"Error starting order execution service: {e}")
