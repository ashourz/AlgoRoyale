import asyncio
from typing import Callable

from algo_royale.application.orders.equity_order_enums import EquityOrderSide
from algo_royale.application.orders.signal_order_payload import SignalOrderPayload
from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.strategies.portfolio_strategy_registry import (
    PortfolioStrategyRegistry,
)
from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.backtester.strategy.portfolio.buffered_components.buffered_portfolio_strategy import (
    BufferedPortfolioStrategy,
)
from algo_royale.logging.loggable import Loggable


class OrderGenerator:
    order_event_type = "ORDER_GENERATED"

    def __init__(
        self,
        signal_generator: SignalGenerator,
        portfolio_strategy_registry: PortfolioStrategyRegistry,
        logger: Loggable,
    ):
        """
        Initialize the OrderGenerator with a trading symbol and an optional logger.

        Args:
            signal_generator (SignalGenerator): The signal generator instance.
            logger (Loggable): Logger for logging events and errors.
        """
        self.logger = logger
        # SIGNAL GENERATOR
        self.signal_generator = signal_generator
        # PORTFOLIO STRATEGY REGISTRY
        self.portfolio_strategy_registry = portfolio_strategy_registry
        # ORDERS
        self.order_lock: asyncio.Lock = asyncio.Lock()
        self.pubsub_orders_map: dict[str, AsyncPubSub] = {}
        self.portfolio_strategy: BufferedPortfolioStrategy = None
        self.signal_roster_subscribers: list[AsyncSubscriber] = []
        self.signal_order_subscribers: dict[str, set[AsyncSubscriber]] = {}
        self.symbols: set[str] = set()
        self.logger.info("OrderGenerator initialized.")

    async def async_subscribe_to_order_events(
        self,
        symbols: list[str],
        callback: Callable[[SignalOrderPayload], None],
        queue_size=1,
    ) -> dict[str, AsyncSubscriber] | None:
        """
        Subscribe to order events for a specific symbol.
        """
        try:
            subscribed_symbols = await self._async_start(symbols=symbols)
            async_subscribers = {}
            for symbol in subscribed_symbols:
                pubsub = self._get_order_pubsub(symbol)
                if not pubsub:
                    self.logger.error(f"No pubsub found for symbol: {symbol}")
                    continue
                self.logger.info(f"Subscribing to order events for {symbol}")
                async_subscribers[symbol] = pubsub.subscribe(
                    event_type=self.order_event_type,
                    callback=callback,
                    queue_size=queue_size,
                )
                if symbol not in self.signal_order_subscribers:
                    self.signal_order_subscribers[symbol] = set()
                self.signal_order_subscribers[symbol].add(async_subscribers[symbol])
                self.logger.info(
                    f"Subscribed to order events for {symbol}: {async_subscribers[symbol]}"
                )
            return async_subscribers
        except Exception as e:
            self.logger.error(f"Error subscribing to order events: {e}")
            return None

    async def async_unsubscribe_from_order_events(
        self, symbol: str, async_subscriber: AsyncSubscriber
    ):
        """
        Unsubscribe from order events for the specified symbols.
        """
        try:
            pubsub = self._get_order_pubsub(symbol)
            if not pubsub:
                self.logger.error(f"No pubsub found for symbol: {symbol}")
                return
            pubsub.unsubscribe(subscriber=async_subscriber)
            self.signal_order_subscribers[symbol].remove(async_subscriber)
            if not self.signal_order_subscribers[symbol]:
                self.signal_order_subscribers.pop(symbol)
            if not any(self.signal_order_subscribers.values()):
                await self._async_stop()
            self.logger.info(f"Unsubscribed from order events for {symbol}")
        except Exception as e:
            self.logger.error(
                f"Error unsubscribing from order events for {symbol}: {e}"
            )

    async def async_restart_stream(self, symbols: list[str]) -> list[str]:
        """
        Restart the order generation stream.
        """
        try:
            await self._async_stop()
            subscribed_symbols = await self._async_start(symbols=symbols)
            return subscribed_symbols
        except Exception as e:
            self.logger.error(f"Error restarting order generation stream: {e}")
            return []

    async def _async_start(self, symbols: list[str]) -> list[str]:
        """
        Start the order generation process for the given symbols.
        """
        try:
            self.logger.info(f"Starting order generation for symbols: {symbols}")
            self.portfolio_strategy = (
                self.portfolio_strategy_registry.get_buffered_portfolio_strategy(
                    symbols=symbols
                )
            )
            if not self.portfolio_strategy:
                self.logger.error(f"No portfolio strategy found for symbols: {symbols}")
                return
            else:
                self.logger.info(
                    f"Using portfolio strategy: {self.portfolio_strategy.get_description()}"
                )
            subscribed_symbols = await self._async_subscribe_to_roster_stream(symbols)
            self.logger.info(
                f"Order generation started for symbols: {subscribed_symbols}"
            )
            # Update internal symbol set
            self.symbols.update(set(subscribed_symbols))
            self.logger.info(f"Internal symbol set updated: {self.symbols}")
            return subscribed_symbols
        except Exception as e:
            self.logger.error(
                f"Error starting order generation for symbols {symbols}: {e}"
            )
            return []

    async def _async_subscribe_to_roster_stream(self, symbols: list[str]) -> list[str]:
        """Subscribe to the signal roster stream to receive updates."""
        try:
            self.logger.info("Subscribing to signal roster stream...")
            # Unsubscribe existing subscribers
            await self._async_unsubscribe_all_subscribers()

            # Subscribe to the signal roster stream
            async def roster_callback(roster):
                await self._async_generate_orders(roster=roster)

            (
                loaded_symbols,
                async_subscriber,
            ) = await self.signal_generator.async_subscribe_to_signals(
                symbols=list(symbols),
                callback=roster_callback,
            )
            if async_subscriber is None:
                self.logger.error("Failed to subscribe to signal roster stream")
                return
            self.signal_roster_subscribers.append(async_subscriber)
            self.logger.info(
                f"Subscribed to signal roster stream with symbols: {loaded_symbols}"
            )
            return loaded_symbols

        except Exception as e:
            self.logger.error(f"Error subscribing to signal stream: {e}")
            return []

    async def _async_generate_orders(self, roster: dict[str, SignalDataPayload]):
        """
        Generate orders based on the provided signal roster.
        """
        try:
            async with self.order_lock:
                # generate order
                await self._async_inner_generate_orders(roster=roster)
        except Exception as e:
            self.logger.error(f"Error generating order: {e}")

    async def _async_inner_generate_orders(self, roster: dict[str, SignalDataPayload]):
        """
        Generate trading orders based on the provided signal roster.
        """
        try:
            if not self.portfolio_strategy:
                self.logger.error("Portfolio strategy is not initialized.")
                return

            # Generate weights based on the signal roster
            df = self.portfolio_strategy.update(roster=roster)
            if df is None:
                self.logger.warning("No valid data to generate orders.")
                return
            weights = df.get("weights", {})
            if not weights:
                self.logger.warning("No weights generated for the portfolio.")
                return

            for symbol, signalDataPayload in roster.items():
                entry_signal = signalDataPayload.signals.get(
                    SignalStrategyColumns.ENTRY_SIGNAL
                )
                exit_signal = signalDataPayload.signals.get(
                    SignalStrategyColumns.EXIT_SIGNAL
                )
                weight = weights.get(symbol, None)
                # Handle entry signal
                if entry_signal == SignalType.BUY.value:
                    # Generate buy order
                    if weight is not None:
                        await self._async_generate_buy_order(
                            symbol, weight, signalDataPayload.price_data
                        )
                # Handle exit signal
                elif exit_signal == SignalType.SELL.value:
                    if weight is not None:
                        await self._async_generate_sell_order(
                            symbol, weight, signalDataPayload.price_data
                        )
        except Exception as e:
            self.logger.error(f"Error generating orders: {e}")

    async def _async_generate_buy_order(
        self, symbol: str, weight: float, price_data: dict
    ):
        """
        Generate a buy order for the given symbol with the specified weight.
        """
        try:
            order_payload = SignalOrderPayload(
                symbol=symbol,
                side=EquityOrderSide.BUY,
                weight=weight,
                price_data=price_data,
            )
            self.logger.info(f"Generated buy order: {order_payload}")
            await self._async_publish_order_event(order_payload)
            self.logger.info(f"Published order event for {symbol}")
        except Exception as e:
            self.logger.error(f"Error generating buy order for {symbol}: {e}")

    async def _async_generate_sell_order(
        self, symbol: str, weight: float, price_data: dict
    ):
        """
        Generate a sell order for the given symbol with the specified weight.
        """
        try:
            order_payload = SignalOrderPayload(
                symbol=symbol,
                side=EquityOrderSide.SELL,
                weight=weight,
                price_data=price_data,
            )
            self.logger.info(f"Generated sell order: {order_payload}")
            await self._async_publish_order_event(order_payload)
            self.logger.info(f"Published order event for {symbol}")
        except Exception as e:
            self.logger.error(f"Error generating sell order for {symbol}: {e}")

    def _get_order_pubsub(self, symbol: str) -> AsyncPubSub:
        """
        Get the pubsub instance for the specified symbol.
        If it does not exist, create a new one.
        """
        if symbol not in self.pubsub_orders_map:
            self.pubsub_orders_map[symbol] = AsyncPubSub()
        return self.pubsub_orders_map[symbol]

    async def _async_publish_order_event(self, order_payload: SignalOrderPayload):
        """
        Publish the generated order event to the appropriate pubsub channel.
        """
        try:
            symbol = order_payload.symbol
            pubsub = self._get_order_pubsub(symbol)
            if not pubsub:
                self.logger.error(f"No pubsub found for symbol: {symbol}")
                return
            await pubsub.async_publish(
                event_type=self.order_event_type, payload=order_payload
            )
            self.logger.info(f"Order event published for {symbol}: {order_payload}")
        except Exception as e:
            self.logger.error(f"Error publishing order event for {symbol}: {e}")

    async def _async_unsubscribe_all_subscribers(self):
        """
        Unsubscribe all subscribers from order events.
        """
        try:
            self.logger.info("Unsubscribing all subscribers from order events...")
            for symbol, subscribers in self.signal_order_subscribers.items():
                for subscriber in subscribers:
                    await self.signal_generator.async_unsubscribe_from_signals(
                        subscriber=subscriber
                    )
        except Exception as e:
            self.logger.error(f"Error unsubscribing all subscribers: {e}")
        finally:
            self.signal_order_subscribers.clear()

    async def _async_stop(self):
        """
        Stop the order generation service.
        """
        try:
            for subscriber in self.signal_roster_subscribers:
                await self.signal_generator.async_unsubscribe_from_signals(
                    subscriber=subscriber
                )
            self.signal_roster_subscribers.clear()
            self.pubsub_orders_map.clear()
            self.portfolio_strategy = None
            self.signal_order_subscribers.clear()
            self.symbols = set()
            self.logger.info("Order generation service stopped.")
        except Exception as e:
            self.logger.error(f"Error stopping order generation service: {e}")
