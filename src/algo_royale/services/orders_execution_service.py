from algo_royale.application.orders.equity_order_enums import EquityOrderSide
from algo_royale.application.orders.equity_order_types import (
    EquityMarketNotionalOrder,
    EquityMarketQtyOrder,
)
from algo_royale.application.orders.signal_order_payload import SignalOrderPayload
from algo_royale.application.symbols.enums import SymbolHoldStatus
from algo_royale.application.symbols.queued_async_symbol_hold import (
    QueuedAsyncSymbolHold,
)
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.logging.loggable import Loggable
from algo_royale.services.ledger_service import LedgerService
from algo_royale.services.order_generator_service import OrderGeneratorService
from algo_royale.services.symbol_hold_service import SymbolHoldService


##TODO: add days to settle to config
class OrderExecutionService:
    def __init__(
        self,
        ledger_service: LedgerService,  ## Service for managing the ledger
        symbol_hold_service: SymbolHoldService,  ## Service for managing symbol holds
        order_generator_service: OrderGeneratorService,  ## Service for generating order payloads
        logger: Loggable,
    ):
        self.ledger_service = ledger_service
        self.symbol_hold_service = symbol_hold_service
        self.symbol_holds = QueuedAsyncSymbolHold(logger=logger)
        self.order_generator_service = order_generator_service
        self.trades_service = ledger_service.trades_service
        self.logger = logger
        self.symbol_order_subscribers: dict[str, list[AsyncSubscriber]] = {}
        self._executor_on: bool = False

    async def start(self, symbols: list[str]) -> dict[str, AsyncSubscriber] | None:
        """Start the order stream adapter to listen for order events."""
        try:
            symbol_subscriber = (
                await self.order_generator_service.subscribe_to_symbol_orders(
                    symbols=symbols, callback=self._handle_order_generation
                )
            )
            if symbol_subscriber:
                for symbol in symbols:
                    self.symbol_order_subscribers.setdefault(symbol, []).append(
                        symbol_subscriber.get(symbol)
                    )
            return symbol_subscriber
        except Exception as e:
            self.logger.error(f"Error starting order stream: {e}")
        return None

    async def stop(self, symbol_subscribers: dict[str, list[AsyncSubscriber]]) -> bool:
        """Stop the order stream adapter."""
        try:
            for symbol, subscribers in symbol_subscribers.items():
                await self.order_generator_service.unsubscribe_from_symbol_orders(
                    symbols=[symbol]
                )
                for subscriber in subscribers:
                    self.symbol_order_subscribers.get(symbol, []).remove(subscriber)
                if not self.symbol_order_subscribers.get(symbol, []):
                    del self.symbol_order_subscribers[symbol]
            return True
        except Exception as e:
            self.logger.error(f"Error stopping order stream: {e}")
            return False

    def update_executor_status(self, status: bool):
        """Update the status of the order executor."""
        try:
            self._executor_on = status
            if status:
                self.logger.info("Order executor is now enabled.")
            else:
                self.logger.info("Order executor is now disabled.")
        except Exception as e:
            self.logger.error(f"Error updating order executor status: {e}")

    async def _async_subscribe_to_symbol_hold(self):
        """Subscribe to the symbol hold stream."""
        try:
            if self.symbol_hold_service:
                self.logger.info("Starting symbol hold subscriber.")
                await self.symbol_hold_service.async_subscribe_to_symbol_holds(
                    callback=self._handle_symbol_hold_event
                )
        except Exception as e:
            self.logger.error(f"Error subscribing to symbol hold stream: {e}")

    def _handle_symbol_hold_event(self, data: SymbolHoldStatus):
        """Handle incoming symbol hold events from the symbol hold stream."""
        try:
            self.logger.info(f"Handling symbol hold event: {data}")
            self.symbol_holds.async_update(data)
        except Exception as e:
            self.logger.error(f"Error handling symbol hold event: {e}")

    def _handle_order_generation(self, data: SignalOrderPayload):
        """Handle incoming order generation events from the order stream."""
        try:
            if self._executor_on is False:
                return
            self.logger.info(f"Handling order generation event: {data}")
            symbol = data.symbol
            hold_status = self.symbol_holds.status[symbol]
            match data.side:
                case EquityOrderSide.BUY:
                    self.logger.info(f"Buy order for symbol {symbol}.")
                    if hold_status is SymbolHoldStatus.BUY_ONLY:
                        self.logger.info(f"Symbol {symbol} is buy-only. Proceeding.")
                        self._submit_buy_order(data)
                    else:
                        self.logger.warning(
                            f"Cannot place buy order for symbol {symbol} as it is in SELL_ONLY hold status."
                        )
                        return
                case EquityOrderSide.SELL:
                    self.logger.info(f"Sell order for symbol {symbol}.")
                    if hold_status is SymbolHoldStatus.SELL_ONLY:
                        self.logger.info(f"Symbol {symbol} is sell-only. Proceeding.")
                        self._submit_sell_order(data)
                    else:
                        self.logger.warning(
                            f"Cannot place sell order for symbol {symbol} as it is in BUY_ONLY hold status."
                        )
                        return
                case _:
                    self.logger.warning(
                        f"Unknown order side for symbol {symbol}: {data.side}"
                    )

        except Exception as e:
            self.logger.error(f"Error handling order generation event: {e}")

    def _submit_buy_order(self, data: SignalOrderPayload):
        """Submit a buy order."""
        try:
            self.logger.info(f"Submitting buy order: {data}")
            # Implement buy order submission logic here
            weighted_notional = self.ledger_service.calculate_weighted_notional(
                data.symbol, data.weight
            )
            self.ledger_service.submit_equity_order(
                order=EquityMarketNotionalOrder(
                    symbol=data.symbol,
                    side=EquityOrderSide.BUY,
                    notional=weighted_notional,
                )
            )
        except Exception as e:
            self.logger.error(f"Error submitting buy order: {e}")

    def _submit_sell_order(self, data: SignalOrderPayload):
        """Submit a sell order."""
        try:
            self.logger.info(f"Submitting sell order: {data}")
            # Implement sell order submission logic here
            current_position = self.ledger_service.get_current_position(data.symbol)
            self.ledger_service.submit_equity_order(
                order=EquityMarketQtyOrder(
                    symbol=data.symbol,
                    side=EquityOrderSide.SELL,
                    quantity=current_position,
                )
            )
        except Exception as e:
            self.logger.error(f"Error submitting sell order: {e}")
