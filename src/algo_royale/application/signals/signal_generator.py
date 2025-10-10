import asyncio
from typing import Any, Callable, Optional

from algo_royale.application.market_data.market_data_enriched_streamer import (
    MarketDataEnrichedStreamer,
)
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.signals.stream_signal_roster_object import (
    StreamSignalRosterObject,
)
from algo_royale.application.strategies.signal_strategy_registry import (
    SignalStrategyRegistry,
)
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.backtester.strategy.signal.combined_weighted_signal_strategy import (
    CombinedWeightedSignalStrategy,
)
from algo_royale.logging.loggable import Loggable


class SignalGenerator:
    signal_event_type = "SIGNAL_GENERATED"

    def __init__(
        self,
        enriched_data_streamer: MarketDataEnrichedStreamer,
        strategy_registry: SignalStrategyRegistry,
        logger: Loggable,
    ):
        self.logger = logger
        self.enriched_data_streamer = enriched_data_streamer
        self.strategy_registry = strategy_registry
        # MARKET DATA
        self.symbol_async_subscriber_map: dict[str, AsyncSubscriber] = {}
        # STRATEGIES
        self.symbol_strategy_map: dict[str, CombinedWeightedSignalStrategy] = {}
        # SIGNALS
        self.symbol_signal_lock_map: dict[str, asyncio.Lock] = {}
        self.signal_roster: StreamSignalRosterObject = StreamSignalRosterObject(
            initial_symbols=[], logger=self.logger
        )
        self.subscribers = []
        self.logger.info("SignalGenerator initialized.")

    async def async_subscribe_to_signals(
        self,
        symbols: list[str],
        callback: Callable[[dict[str, SignalDataPayload], type], Any],
        queue_size=1,
    ) -> tuple[list[str], Optional[AsyncSubscriber]]:
        """
        Subscribe to signals for a specific symbol.

        :param symbol: The symbol to subscribe to.
        :param callback: The callback function to call with the generated signals.
        """
        try:
            loaded_symbols = await self._async_start(symbols=symbols)
            subscriber = self.signal_roster.subscribe(
                callback=callback,
                queue_size=queue_size,
            )
            self.subscribers.append(subscriber)
            self.logger.info(f"Subscribed to signals for symbols: {loaded_symbols}")
            return (loaded_symbols, subscriber)
        except Exception as e:
            self.logger.error(f"Error subscribing to signals: {e}")
            return ([], None)

    async def async_unsubscribe_from_signals(self, subscriber: AsyncSubscriber):
        """
        Unsubscribe from signals for a specific subscriber.

        :param subscriber: The subscriber to unsubscribe from.
        """
        try:
            self.signal_roster.unsubscribe(subscriber=subscriber)
            self.subscribers.remove(subscriber)
            if not self.subscribers:
                # No subscribers left, need to run async_stop
                await self._async_stop()
        except Exception as e:
            self.logger.error(f"Error unsubscribing from signals: {e}")

    async def async_restart_stream(self) -> list[str] | None:
        """
        Restart the signal generation stream.
        """
        try:
            await self._async_stop()
            return await self._async_start()
        except Exception as e:
            self.logger.error(f"Error restarting signal stream: {e}")
            return None

    async def _async_start(self, symbols: list[str]) -> list[str]:
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            loaded_symbols = self._load_symbol_strategies(symbols=symbols)
            self._initialize_symbol_signal_lock(symbols=loaded_symbols)
            await self._async_subscribe_to_enriched_streams(symbols=loaded_symbols)
            self.logger.info(
                f"Signal generation service started for symbols: {loaded_symbols}."
            )
            return loaded_symbols
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")
            return []

    def _load_symbol_strategies(self, symbols: list[str]) -> list[str]:
        """
        Load symbol strategies from the strategy registry.
        """
        try:
            signals_with_strategies = []
            for symbol in symbols:
                if self.symbol_strategy_map.get(symbol) is None:
                    self.logger.debug(f"Loading strategies for symbol: {symbol}")
                    self.symbol_strategy_map[symbol] = (
                        self.strategy_registry.get_combined_weighted_signal_strategy(
                            symbol=symbol
                        )
                    )
                    if self.symbol_strategy_map.get(symbol) is None:
                        self.logger.debug(f"Loading strategies for symbol: {symbol}")
                        strategy = self.strategy_registry.get_combined_weighted_signal_strategy(
                            symbol=symbol
                        )
                        if strategy is None:
                            self.logger.warning(
                                f"No strategy found for symbol: {symbol}. It will be skipped."
                            )
                            # Do not add to symbol_strategy_map
                        else:
                            self.symbol_strategy_map[symbol] = strategy
                            signals_with_strategies.append(symbol)
                            self.logger.info(
                                f"Symbol strategies loaded successfully for {symbol}: {strategy}."
                            )
                    else:
                        signals_with_strategies.append(symbol)
                        self.logger.info(
                            f"Symbol strategies loaded successfully for {symbol}: {self.symbol_strategy_map[symbol]}."
                        )
                else:
                    signals_with_strategies.append(symbol)
                    self.logger.info(
                        f"Symbol strategies already loaded for {symbol}: {self.symbol_strategy_map[symbol]}."
                    )
            if not signals_with_strategies:
                self.logger.warning(
                    f"No valid strategies found for any of the requested symbols: {symbols}. Signal generation will not proceed."
                )
            return signals_with_strategies
        except Exception as e:
            self.logger.error(f"Error loading symbol strategies: {e}")
            return []

    def _initialize_symbol_signal_lock(self, symbols: list[str]):
        """
        Initialize locks for each symbol to ensure thread-safe signal generation.
        """
        try:
            for symbol in symbols:
                if symbol not in self.symbol_signal_lock_map:
                    self.symbol_signal_lock_map[symbol] = asyncio.Lock()
                    self.logger.debug(f"Initialized lock for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error initializing symbol signal locks: {e}")

    async def _async_subscribe_to_enriched_streams(self, symbols: list[str]):
        """
        Subscribe to the enriched stream for a list of symbols.
        This will allow the signal generator to receive real-time data updates for all symbols at once.
        """
        try:
            self.logger.debug(f"Subscribing to enriched stream for symbols: {symbols}")

            async def enriched_data_callback(enriched_data):
                # Extract symbol from enriched_data if possible, otherwise iterate
                symbol = (
                    enriched_data.get("symbol")
                    if isinstance(enriched_data, dict) and "symbol" in enriched_data
                    else None
                )
                if symbol and symbol in self.symbol_strategy_map:
                    await self._async_generate_signal(symbol, enriched_data)
                else:
                    # fallback: try all symbols
                    for sym in symbols:
                        await self._async_generate_signal(sym, enriched_data)

            symbol_subscriber_map = (
                await self.enriched_data_streamer.async_subscribe_to_enriched_data(
                    symbols=symbols,
                    callback=enriched_data_callback,
                )
            )
            if symbol_subscriber_map is None:
                self.logger.error(
                    f"Failed to subscribe to enriched stream for symbols: {symbols}"
                )
                return
            for symbol, async_subscriber in symbol_subscriber_map.items():
                self.symbol_async_subscriber_map[symbol] = async_subscriber
                self.logger.info(f"Subscribed to enriched stream for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error initializing enriched stream subscriptions: {e}")

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

    async def _async_unsubscribe_from_enriched_data(self):
        """
        Unsubscribe from all enriched data streams.
        """
        try:
            symbol_subscribers = {
                symbol: [async_subscriber]
                for symbol, async_subscriber in self.symbol_async_subscriber_map.items()
            }
            await self.enriched_data_streamer.async_unsubscribe_from_enriched_data(
                symbol_subscribers=symbol_subscribers
            )
            self.logger.info("Unsubscribed from all enriched data streams")
        except Exception as e:
            self.logger.error(
                f"Error unsubscribing from all enriched data streams: {e}"
            )
        finally:
            self.symbol_async_subscriber_map.clear()

    async def _async_unsubscribe_all_subscribers(self):
        """
        Unsubscribe from all signal roster streams.
        """
        try:
            for subscriber in self.subscribers:
                self.signal_roster.unsubscribe(subscriber)
                self.logger.info(
                    f"Unsubscribed from enriched data stream: {subscriber}"
                )
        except Exception as e:
            self.logger.error(
                f"Error unsubscribing from all enriched data streams: {e}"
            )
        finally:
            self.subscribers.clear()

    async def _async_stop(self):
        """
        Stop the signal generation service.
        """
        try:
            await self._async_unsubscribe_all_subscribers()
            await self.signal_roster.async_shutdown()
            self.signal_roster = StreamSignalRosterObject(
                initial_symbols=[], logger=self.logger
            )
            self.symbol_strategy_map.clear()
            await self._async_unsubscribe_from_enriched_data()
            self.logger.info("Signal generation service stopped.")
        except Exception as e:
            self.logger.error(f"Error stopping signal generation: {e}")
