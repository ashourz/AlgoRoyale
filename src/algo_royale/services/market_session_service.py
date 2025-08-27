from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.logging.loggable import Loggable
from algo_royale.services.ledger_service import LedgerService
from algo_royale.services.order_monitor_service import OrderMonitorService
from algo_royale.services.orders_execution_service import OrderExecutionServices
from algo_royale.services.orders_service import OrderService
from algo_royale.services.positions_service import PositionsService
from algo_royale.services.symbol_hold_service import SymbolHoldService
from algo_royale.services.symbol_service import SymbolService
from algo_royale.services.trades_service import TradesService


class MarketSessionService:
    END_STATUS = [SymbolHoldStatus.PENDING_SETTLEMENT, SymbolHoldStatus.CLOSED_FOR_DAY]

    def __init__(
        self,
        order_service: OrderService,
        positions_service: PositionsService,
        symbol_service: SymbolService,
        symbol_hold_service: SymbolHoldService,
        trade_service: TradesService,
        ledger_service: LedgerService,
        order_execution_service: OrderExecutionServices,
        order_monitor_service: OrderMonitorService,
        logger: Loggable,
    ):
        ## SYMBOLS
        self.symbol_service = symbol_service
        self.symbol_hold_service = symbol_hold_service
        self.symbol_subscribers: dict[str, AsyncSubscriber] = {}
        self.symbol_hold_subscriber: AsyncSubscriber = None
        self.symbol_holds: dict[str, SymbolHoldStatus] = {}
        ## ORDERS
        self.order_service = order_service
        self.order_execution_service = order_execution_service
        self.order_monitor_service = order_monitor_service
        ## POSITIONS
        self.positions_service = positions_service
        ## TRADES
        self.trade_service = trade_service
        ## LEDGER
        self.ledger_service = ledger_service
        ## PROCESS
        self.premarket_completed = False
        ## LOGGER
        self.logger = logger

    async def async_start_premarket(self) -> None:
        """Start the pre-market session."""
        try:
            self.logger.info("Starting pre-market session...")
            self.trade_service.update_settled_trades()
            self.order_service.update_settled_orders()
            self.symbol_hold_service.start()
            await self._async_subscribe_to_symbol_holds()
            await self._async_run_validations()
            self._init_ledger_service()
            await self.order_monitor_service.async_start()
            await self._async_start_order_execution_subscription()
            self.premarket_completed = True
            self.logger.info("Pre-market session started.")
        except Exception as e:
            self.logger.error(f"Error starting pre-market session: {e}")

    async def async_start_market(self) -> dict[str, AsyncSubscriber] | None:
        """Start the market session."""
        try:
            if not self.premarket_completed:
                self.logger.warning(
                    "Pre-market session has not been completed. Starting pre-market session..."
                )
                await self.async_start_premarket()
            self.logger.info("Starting market session...")
            self.order_execution_service.update_executor_status(True)
            self.logger.info("Market session started.")
        except Exception as e:
            self.logger.error(f"Error starting market session: {e}")
        return None

    async def async_stop_market(self) -> None:
        """Stop the market session."""
        try:
            self.logger.info("Stopping market session...")
            await self._async_stop_order_execution()
            await self._async_unsubscribe_from_symbol_holds()
            self.symbol_hold_service.stop()
            await self.order_monitor_service.async_stop()
            await self._async_run_validations()
            self.premarket_completed = False
            self.logger.info("Market session stopped.")
        except Exception as e:
            self.logger.error(f"Error stopping market session: {e}")

    def _init_ledger_service(self) -> None:
        """Initialize the ledger service."""
        try:
            available_cash = self.ledger_service.get_available_cash()
            self.ledger_service.init_sod_cash(available_cash)
        except Exception as e:
            self.logger.error(f"Error initializing ledger service: {e}")

    async def _async_start_order_execution_subscription(self) -> None:
        """Start the order execution services."""
        try:
            symbols = await self.symbol_service.async_get_symbols()
            symbol_subscribers = await self.order_execution_service.start(symbols)
            if symbol_subscribers:
                for symbol, subscriber in symbol_subscribers.items():
                    self.symbol_subscribers[symbol] = subscriber
                    return True
            else:
                self.logger.error("Failed to start order execution service.")
        except Exception as e:
            self.logger.error(f"Error starting order execution service: {e}")
        return False

    async def _async_stop_order_execution(self) -> None:
        """Stop the order execution services."""
        try:
            self.order_execution_service.update_executor_status(False)
            if self.symbol_subscribers:
                await self.order_execution_service.stop(
                    symbol_subscribers=self.symbol_subscribers
                )
        except Exception as e:
            self.logger.error(f"Error stopping order execution service: {e}")
        finally:
            self.symbol_subscribers.clear()

    async def _async_run_validations(self) -> None:
        """Run all necessary validations."""
        try:
            await self.trade_service.reconcile_trades()
            await self.positions_service.validate_positions()
        except Exception as e:
            self.logger.error(f"Error running validations: {e}")

    async def _async_subscribe_to_symbol_holds(self) -> None:
        """Subscribe to symbol holds."""
        try:
            async_subscriber = (
                await self.symbol_hold_service.async_subscribe_to_hold_roster(
                    callback=self._async_handle_symbol_hold_roster_event
                )
            )

            if async_subscriber:
                self.symbol_hold_subscriber = async_subscriber
                return True
            else:
                self.logger.error("Failed to subscribe to symbol holds.")

        except Exception as e:
            self.logger.error(f"Error subscribing to symbol holds: {e}")
        return False

    async def _async_unsubscribe_from_symbol_holds(self) -> None:
        """Unsubscribe from symbol holds."""
        try:
            if self.symbol_hold_subscriber:
                await self.symbol_hold_service.unsubscribe_from_symbol_holds()
        except Exception as e:
            self.logger.error(f"Error unsubscribing from symbol holds: {e}")
        finally:
            self.symbol_hold_subscriber = None

    async def _async_handle_symbol_hold_roster_event(
        self, symbol_hold_roster: dict[str, SymbolHoldStatus]
    ) -> None:
        """Handle symbol hold events."""
        try:
            if symbol_hold_roster and all(
                status in self.END_STATUS for status in symbol_hold_roster.values()
            ):
                # All symbols are in an end status, do your logic here
                self.logger.info(
                    "All symbol holds are in END_STATUS. Force stopping..."
                )
                await self.async_force_stop()
        except Exception as e:
            self.logger.error(f"Error handling symbol hold event: {e}")
