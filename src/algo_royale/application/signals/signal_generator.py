import asyncio
from typing import Any, Callable

from algo_royale.application.market_data.market_data_enriched_streamer import (
    MarketDataEnrichedStreamer,
)
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.signals.stream_signal_roster_object import (
    StreamSignalRosterObject,
)
from algo_royale.application.strategies.strategy_registry import StrategyRegistry
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.backtester.strategy.signal.combined_weighted_signal_strategy import (
    CombinedWeightedSignalStrategy,
)
from algo_royale.logging.loggable import Loggable


class SignalGenerator:
    signal_event_type = "SIGNAL_GENERATED"

    def __init__(
        self,
        symbol_manager: SymbolManager,
        enriched_data_streamer: MarketDataEnrichedStreamer,
        strategy_registry: StrategyRegistry,
        logger: Loggable,
    ):
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.enriched_data_streamer = enriched_data_streamer
        self.strategy_registry = strategy_registry
        # MARKET DATA
        self.symbol_async_subscriber_map: dict[str, AsyncSubscriber] = {}
        # STRATEGIES
        self.symbol_strategy_map: dict[str, CombinedWeightedSignalStrategy] = {}
        # SIGNALS
        self.symbol_signal_lock_map: dict[str, asyncio.Lock] = {}
        self.signal_roster: StreamSignalRosterObject | None = None
        self.logger.info("SignalGenerator initialized.")

    async def async_start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            symbols = await self.symbol_manager.async_get_symbols()
            self.logger.info("Loading symbol strategies...")
            self._load_symbol_strategies(symbols=symbols)
            self.logger.info("Initializing symbol signal locks...")
            self._initialize_symbol_signal_lock(symbols=symbols)
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_enriched_streams(symbols=symbols)
            self.logger.info("Creating signal roster object...")
            self.signal_roster = StreamSignalRosterObject(
                initial_symbols=symbols, logger=self.logger
            )
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

    def _load_symbol_strategies(self, symbols: list[str]):
        """
        Load symbol strategies from the strategy registry.
        """
        try:
            for symbol in symbols:
                self.logger.debug(f"Loading strategies for symbol: {symbol}")
                self.symbol_strategy_map[symbol] = (
                    self.strategy_registry.get_combined_weighted_signal_strategy(
                        symbol=symbol
                    )
                )
            self.logger.info("Symbol strategies loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading symbol strategies: {e}")

    def _initialize_symbol_signal_lock(self, symbols: list[str]):
        """
        Initialize locks for each symbol to ensure thread-safe signal generation.
        """
        for symbol in symbols:
            if symbol not in self.symbol_signal_lock_map:
                self.symbol_signal_lock_map[symbol] = asyncio.Lock()
            self.logger.debug(f"Initialized lock for symbol: {symbol}")
        else:
            self.logger.debug(f"Lock already exists for symbol: {symbol}")

    def _subscribe_to_enriched_streams(self, symbols: list[str]):
        """
        Subscribe to the enriched stream for a specific symbol.
        This will allow the signal generator to receive real-time data updates.
        """
        try:
            for symbol in symbols:
                self.logger.debug(
                    f"Subscribing to enriched stream for symbol: {symbol}"
                )

                async_subscriber = (
                    self.enriched_data_streamer.subscribe_to_enriched_data(
                        symbol=symbol,
                        callback=lambda enriched_data,
                        symbol=symbol: self._async_generate_signal(
                            symbol=symbol, enriched_data=enriched_data
                        ),
                    )
                )
                self.symbol_async_subscriber_map[symbol] = async_subscriber
                self.logger.info(f"Subscribed to enriched stream for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error subscribing to enriched stream for {symbol}: {e}")

    async def _async_generate_signal(self, symbol: str, enriched_data: dict):
        """
        Generate a trading signal based on the provided data and strategy.

        :param symbol: The symbol for which to generate the signal.
        :return: None if no strategy is found, otherwise publishes the generated signals.
        """
        try:
            if symbol not in self.symbol_strategy_map:
                self.logger.warning(f"No strategy found for symbol: {symbol}")
                return

            lock = self.symbol_signal_lock_map.get(symbol)
            if lock is None:
                self.logger.error(f"No lock found for symbol: {symbol}")
                return

            async with lock:
                # generate signal
                await self._async_generate_signal_inner(symbol, enriched_data)
        except Exception as e:
            self.logger.error(f"Error generating signal for {symbol}: {e}")

    async def _async_generate_signal_inner(self, symbol: str, enriched_data: dict):
        try:
            strategy = self.symbol_strategy_map[symbol]
            # Validation
            if strategy is None:
                self.logger.error(f"No strategy found for symbol: {symbol}")
                return
            if not enriched_data:
                self.logger.warning(f"No data provided for symbol: {symbol}")
                return

            self.logger.debug(
                f"Generating signals for {symbol} with data: {enriched_data}"
            )
            signals = strategy.generate_signals(enriched_data)
            self.logger.debug(f"[{symbol}] Generated signals: {signals}")
            if signals is None or signals.empty:
                self.logger.warning(f"No signals generated for symbol: {symbol}")
                return
            else:
                payload = SignalDataPayload(signals=signals, price_data=enriched_data)
                await self.signal_roster.async_set_signal_data_payload(
                    symbol=symbol, payload=payload
                )
                self.logger.info(
                    f"Signals generated and set for symbol: {symbol}, signals: {signals}"
                )
        except Exception as e:
            self.logger.error(f"Error generating signals for {symbol}: {e}")

    def subscribe_to_signals(
        self,
        callback: Callable[[dict[str, SignalDataPayload], type], Any],
        queue_size=1,
    ) -> AsyncSubscriber:
        """
        Subscribe to signals for a specific symbol.

        :param symbol: The symbol to subscribe to.
        :param callback: The callback function to call with the generated signals.
        """
        return self.signal_roster.subscribe(
            callback=callback,
            queue_size=queue_size,
        )

    def unsubscribe_from_signals(self, subscriber: AsyncSubscriber):
        """
        Unsubscribe from signals for a specific subscriber.

        :param subscriber: The subscriber to unsubscribe from.
        """
        try:
            self.signal_roster.unsubscribe(subscriber=subscriber)
        except Exception as e:
            self.logger.error(f"Error unsubscribing from signals: {e}")

    def _unsubscribe_from_enriched_data(self):
        """
        Unsubscribe from all enriched data streams for all symbols.
        """
        try:
            for symbol, async_subscriber in self.symbol_async_subscriber_map.items():
                self.enriched_data_streamer.unsubscribe_from_enriched_data(
                    symbol, async_subscriber
                )
                self.logger.info(f"Unsubscribed from {symbol} enriched data stream")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from enriched data streams: {e}")
        self.symbol_async_subscriber_map.clear()

    async def async_stop(self):
        """
        Stop the signal generation service.
        """
        try:
            self.logger.info("Stopping signal generation service...")
            await self.signal_roster.async_shutdown()
            self.logger.info("Signal generation stopped.")
            self.symbol_strategy_map.clear()
            self.logger.info("Symbol strategy map cleared.")
            self._unsubscribe_from_enriched_data()
            self.logger.info("Unsubscribed from all enriched data streams.")
        except Exception as e:
            self.logger.error(f"Error stopping signal generation: {e}")
