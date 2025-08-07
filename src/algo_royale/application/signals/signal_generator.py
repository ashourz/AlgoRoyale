import asyncio
from typing import Any, Callable

from algo_royale.application.market_data.market_data_streamer import MarketDataStreamer
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.strategies.strategy_registry import StrategyRegistry
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.backtester.strategy.signal.combined_weighted_signal_strategy import (
    CombinedWeightedSignalStrategy,
)
from algo_royale.events.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.logging.loggable import Loggable


class SignalGenerator:
    signal_event_type = "SIGNAL_GENERATED"

    def __init__(
        self,
        symbol_manager: SymbolManager,
        market_data_streamer: MarketDataStreamer,
        strategy_registry: StrategyRegistry,
        logger: Loggable,
    ):
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.market_data_streamer = market_data_streamer
        self.strategy_registry = strategy_registry
        # MARKET DATA
        self.symbol_async_subscriber_map: dict[str, AsyncSubscriber] = {}
        # STRATEGIES
        self.symbol_strategy_map: dict[str, CombinedWeightedSignalStrategy] = {}
        # SIGNALS
        self.pubsub_signal_map: dict[str, AsyncPubSub] = {}
        self.symbol_signal_lock_map: dict[str, asyncio.Lock] = {}
        self.logger.info("SignalGenerator initialized.")

    async def start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            symbols = await self.symbol_manager.async_get_symbols()
            self.logger.info("Loading symbol strategies...")
            self._load_symbol_strategies()
            self.logger.info("Initializing symbol signal locks...")
            self._initialize_symbol_signal_lock()
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_market_streams()
            self.logger.info(f"Starting signal generation | symbols: {symbols}")
            self.stream_service.start_stream(symbols=symbols, on_quote=self._onQuote)
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

    def _subscribe_to_market_streams(self, symbols: list[str]):
        """
        Subscribe to the market stream for a specific symbol.
        This will allow the signal generator to receive real-time data updates.
        """
        try:
            for symbol in symbols:
                self.logger.debug(f"Subscribing to stream for symbol: {symbol}")

                async_subscriber = self.market_data_streamer.subscribe_to_stream(
                    symbol=symbol,
                    callback=lambda data: self._async_generate_signal(
                        symbol=symbol, data=data
                    ),
                )
                self.symbol_async_subscriber_map[symbol] = async_subscriber
                self.logger.info(f"Subscribed to market stream for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error subscribing to market stream for {symbol}: {e}")

    def _generate_signal(self, symbol: str, data: dict):
        strategy = self.symbol_strategy_map[symbol]
        # Validation
        if strategy is None:
            self.logger.error(f"No strategy found for symbol: {symbol}")
            return
        if not data:
            self.logger.warning(f"No data provided for symbol: {symbol}")
            return

        self.logger.debug(f"Generating signals for {symbol} with data: {data}")
        signals = strategy.generate_signals(data)
        self.logger.debug(f"[{symbol}] Generated signals: {signals}")
        if signals is None or signals.empty:
            self.logger.warning(f"No signals generated for symbol: {symbol}")
            return
        else:
            pubsub = self.pubsub_signal_map.get(symbol)
            if pubsub is None:
                self.logger.error(f"No pubsub found for symbol: {symbol}")
                return
            payload = SignalDataPayload(signals=signals, price_data=data)
            pubsub.async_publish(event_type=self.signal_event_type, data=payload)
            self.logger.info(f"Published signals for {symbol} to pubsub")

    async def _async_generate_signal(self, symbol: str, data: dict):
        """
        Generate a trading signal based on the provided data and strategy.

        :param symbol: The symbol for which to generate the signal.
        :return: None if no strategy is found, otherwise publishes the generated signals.
        """
        try:
            if symbol not in self.symbol_strategy_map:
                self.logger.warning(f"No strategy found for symbol: {symbol}")
                return

            data_ingest_object = self.stream_data_ingest_object_map.get(symbol)
            if data_ingest_object is None:
                self.logger.error(f"No data ingest object found for symbol: {symbol}")
                return

            lock = self.symbol_signal_lock_map.get(symbol)
            if lock is None:
                self.logger.error(f"No lock found for symbol: {symbol}")
                return

            async with lock:
                # generate signal
                self._generate_signal(symbol, data)
        except Exception as e:
            self.logger.error(
                f"Error generating signal for {data_ingest_object.symbol}: {e}"
            )
            return

    ##TODO: THIS SUBSCRIPTION SHOULD RETURN SIGNAL DATA PAYLOAD FOR ALL AVAILABLE SYMBOLS AT ONCE
    def subscribe_to_signals(
        self, symbol: str, callback: Callable[[dict], Any], queue_size=1
    ):
        """
        Subscribe to signals for a specific symbol.

        :param symbol: The symbol to subscribe to.
        :param callback: The callback function to call with the generated signals.
        """
        pubsub = self.pubsub_signal_map.get(symbol)
        if pubsub is None:
            self.logger.error(f"No pubsub found for symbol: {symbol}")
            return
        pubsub.subscribe(
            event_type=self.signal_event_type, callback=callback, queue_size=queue_size
        )

    def unsubscribe_from_signals(self, symbol: str, subscriber: AsyncSubscriber):
        """
        Unsubscribe from signals for a specific symbol.

        :param symbol: The symbol to unsubscribe from.
        """
        pubsub = self.pubsub_signal_map.get(symbol)
        if pubsub is None:
            self.logger.error(f"No pubsub found for symbol: {symbol}")
            return
        pubsub.unsubscribe(subscriber)

    def _unsubscribe_from_market_data(self):
        """
        Unsubscribe from all market data streams for all symbols.
        """
        for symbol, async_subscriber in self.symbol_async_subscriber_map.items():
            self.market_data_streamer.unsubscribe_from_stream(symbol, async_subscriber)
            self.logger.info(f"Unsubscribed from {symbol} market data stream")
        self.symbol_async_subscriber_map.clear()

    def stop(self):
        """
        Stop the signal generation service.
        """
        try:
            self.logger.info("Stopping signal generation...")
            self.stream_service.stop_stream()
            self.logger.info("Signal generation stopped.")
            self.symbol_strategy_map.clear()
            self.logger.info("Symbol strategy map cleared.")
            self._unsubscribe_from_market_data()
            self.logger.info("Unsubscribed from all market data streams.")
        except Exception as e:
            self.logger.error(f"Error stopping signal generation: {e}")
