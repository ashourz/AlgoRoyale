from typing import Any, Callable, Dict, List
from uuid import UUID

from algo_royale.adapters.market_data.stream_adapter import StreamAdapter
from algo_royale.application.signals.stream_data_ingest_object import (
    StreamDataIngestObject,
)
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_stream_bar import StreamBar
from algo_royale.models.alpaca_market_data.alpaca_stream_quote import StreamQuote
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.repo.data_stream_session_repo import DataStreamSessionRepo
from algo_royale.utils.clock_provider import ClockProvider


class MarketDataRawStreamer:
    """
    MarketDataStreamer is responsible for managing the streaming of market data
    for various stock symbols. It initializes stream data ingest objects for each
    symbol and subscribes to the relevant market data feeds.
    """

    def __init__(
        self,
        stream_adapter: StreamAdapter,
        data_stream_session_repo: DataStreamSessionRepo,
        logger: Loggable,
        clock_provider: ClockProvider,
        is_live: bool = False,
    ):
        self.stream_adapter = stream_adapter
        self.data_stream_session_repo = data_stream_session_repo
        self.stream_data_ingest_object_map: dict[str, StreamDataIngestObject] = {}
        self.upstream_subscriber_map: Dict[str, list[AsyncSubscriber]] = {}
        self.symbol_data_stream_session_ids: dict[str, UUID] = {}
        self.logger = logger
        self.is_live = is_live
        self.clock_provider = clock_provider

    ## Subscribe Methods
    async def subscribe(
        self, symbols: List[str], callback: Callable
    ) -> Dict[str, AsyncSubscriber]:
        result = {}
        for symbol in symbols:
            if not self._can_subscribe(symbol):
                continue
            # Create a new subscriber for the symbol
            subscriber = await self._create_subscriber(symbol, callback)
            if subscriber:
                if symbol not in self.upstream_subscriber_map:
                    self.upstream_subscriber_map[symbol] = []
                self.upstream_subscriber_map[symbol].append(subscriber)
                result[symbol] = subscriber
            else:
                self.logger.error(f"Failed to create subscriber for symbol: {symbol}")
        # Return the result mapping of symbols to their subscribers
        return result

    def _can_subscribe(self, symbol):
        return True

    async def _create_subscriber(
        self, symbol: str, callback: Callable
    ) -> AsyncSubscriber | None:
        """
        Create a subscriber for the specified symbol and callback.
        This will start the signal generator for the symbol if not already started.
        :param symbol: The stock symbol to subscribe to.
        :param callback: The callback function to handle incoming data.
        """
        try:
            stream_started = await self._async_start_streaming_symbol(symbol=symbol)
            if not stream_started:
                self.logger.error(f"Failed to start stream for symbol: {symbol}")
                return None
            subscriber = self._subscribe_to_stream_data_ingest_object(symbol, callback)
            if subscriber:
                if symbol not in self.upstream_subscriber_map:
                    self.upstream_subscriber_map[symbol] = []
                self.upstream_subscriber_map[symbol].append(subscriber)
                self.logger.info(f"Subscribed to stream for symbol: {symbol}")
            else:
                self.logger.error(f"Failed to subscribe to stream for symbol: {symbol}")
            return subscriber
        except Exception as e:
            self.logger.error(f"Error subscribing to stream for {symbol}: {e}")
            return None

    async def _async_start_streaming_symbol(self, symbol: str) -> bool:
        """
        Start the market data stream for the specified symbol.
        This will initialize the stream data ingest object and subscribe to the market data feed.
        :param symbol: The stock symbol to start streaming data for.
        :return: True if the stream was started successfully, False otherwise.
        """
        try:
            self.logger.info(f"Starting signal generation for symbol {symbol}...")
            if self._should_add_symbol(symbol):
                self.logger.info(f"Symbol {symbol} not in stream, adding it.")
                if self._is_stream_started():
                    await self.stream_adapter.async_add_symbols(
                        quotes=[symbol], bars=[symbol]
                    )
                    self.logger.info(f"Added symbol {symbol} to stream.")
                else:
                    feed = DataFeed.SIP if self.is_live else DataFeed.IEX
                    await self.stream_adapter.async_start_stream(
                        symbols=[symbol],
                        feed=feed,
                        on_quote=self._onQuote,
                        on_bar=self._onBar,
                    )
                    self.logger.info(f"Started stream for symbol: {symbol}")
                session_uuid = self._start_data_stream_session(symbol)
                if session_uuid:
                    self.logger.info(
                        f"Started data stream session for symbol: {symbol}"
                    )
                else:
                    self.logger.warning(
                        f"Failed to start data stream session for symbol: {symbol}"
                    )
                    ## TODO: Consider stopping the stream if session start fails
            else:
                self.logger.info(f"Symbol {symbol} already in stream, not adding.")
            return True
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")
        return False

    def _should_add_symbol(self, symbol: str) -> bool:
        """Return symbols that are not already in the stream."""
        current_stream_symbols = self.stream_adapter.get_stream_symbols()
        bar_symbols = set(current_stream_symbols.bars)
        quote_symbols = set(current_stream_symbols.quotes)
        should_add_to_bar = symbol not in bar_symbols
        should_add_to_quote = symbol not in quote_symbols
        return should_add_to_bar | should_add_to_quote

    def _is_stream_started(self) -> bool:
        """Check if the stream is currently started."""
        current_stream_symbols = self.stream_adapter.get_stream_symbols()
        return any(current_stream_symbols.bars) or any(current_stream_symbols.quotes)

    async def _onQuote(self, raw_quote: Any):
        """
        Handle incoming market quotes and generate signals.

        :param quote: The market quote data.
        """
        try:
            self.logger.debug(f"Received raw quote: {raw_quote}")
            quote = StreamQuote.from_raw(raw_quote)
            self.logger.info(f"Received quote: {quote}")
            await self.stream_data_ingest_object_map[
                quote.symbol
            ].async_update_with_quote(quote)
            self.logger.debug(f"Updated stream data ingest object for {quote.symbol}")

        except Exception as e:
            self.logger.error(f"Error processing quote: {e}")

    async def _onBar(self, raw_bar: Any):
        """
        Handle incoming market bars and generate signals.

        :param bar: The market bar data.
        """
        try:
            self.logger.debug(f"Received raw bar: {raw_bar}")
            bar = StreamBar.from_raw(raw_bar)
            self.logger.info(f"Received bar: {bar}")
            await self.stream_data_ingest_object_map[bar.symbol].async_update_with_bar(
                bar
            )
            self.logger.debug(f"Updated stream data ingest object for {bar.symbol}")
        except Exception as e:
            self.logger.error(f"Error processing bar: {e}")

    def _start_data_stream_session(self, symbol: str) -> UUID | None:
        """Start a new data stream session for the specified symbol."""
        try:
            session_uuid = self.data_stream_session_repo.insert_data_stream_session(
                stream_class_name="MarketDataRawStreamer",
                symbol=symbol,
                start_time=self.clock_provider.now(),
            )
            self.symbol_data_stream_session_ids[symbol] = session_uuid
            return session_uuid
        except Exception as e:
            self.logger.error(f"Error starting data stream session for {symbol}: {e}")
            return None

    def _subscribe_to_stream_data_ingest_object(
        self, symbol: str, callback: Callable
    ) -> AsyncSubscriber | None:
        """Get the stream data ingest object for the specified symbol."""
        try:
            if symbol not in self.stream_data_ingest_object_map:
                self.logger.debug(
                    f"Creating StreamDataIngestObject for symbol: {symbol}"
                )
                self.stream_data_ingest_object_map[symbol] = StreamDataIngestObject(
                    symbol
                )
            else:
                self.logger.debug(
                    f"StreamDataIngestObject already exists for symbol: {symbol}"
                )
            return self.stream_data_ingest_object_map[symbol].subscribe(
                callback=callback
            )
        except Exception as e:
            self.logger.error(
                f"Error subscribing to StreamDataIngestObject for {symbol}: {e}"
            )
            return None

    ## Unsubscribe Methods
    async def unsubscribe(self, subscribers: List[AsyncSubscriber]) -> List[str]:
        """
        Unsubscribe a list of subscribers from all symbols they are registered to.
        Streaming for a symbol is stopped only when no subscribers remain for that symbol.
        Returns a list of symbols that were fully unsubscribed (stream stopped and cleaned up).
        """
        unsubscribed_symbols = []
        try:
            self.logger.info(f"Unsubscribing {len(subscribers)} subscribers...")
            for subscriber in subscribers:
                symbols = [
                    symbol
                    for symbol, subs in self.upstream_subscriber_map.items()
                    if subscriber in subs
                ]
                for symbol in symbols:
                    self.upstream_subscriber_map[symbol].remove(subscriber)
                    self.logger.info(
                        f"Unsubscribed subscriber {subscriber} from symbol: {symbol}"
                    )
                    # If no subscribers remain, stop streaming and clean up
                    if not self.upstream_subscriber_map[symbol]:
                        self.logger.info(
                            f"No subscribers remain for symbol: {symbol}. Stopping stream."
                        )
                        await self._async_stop_streaming_symbol(symbol)
                        self.stream_data_ingest_object_map[symbol].unsubscribe()
                        self._stop_data_stream_session(symbol)
                        self.upstream_subscriber_map.pop(symbol)
                        unsubscribed_symbols.append(symbol)
        except Exception as e:
            self.logger.error(f"Error unsubscribing subscribers: {e}")
        return unsubscribed_symbols

    def _stop_data_stream_session(self, symbol: str):
        """Stop the data stream session for the specified symbol."""
        try:
            if symbol in self.symbol_data_stream_session_ids:
                session_id = self.symbol_data_stream_session_ids.pop(symbol)
                self.data_stream_session_repo.update_data_stream_session_end_time(
                    session_id=session_id,
                    end_time=self.clock_provider.now(),
                )
        except Exception as e:
            self.logger.error(f"Error stopping data stream session for {symbol}: {e}")

    async def _async_stop_streaming_symbol(self, symbol: str):
        """
        Stop the market data stream for the specified symbol ONLY if no subscribers remain.
        """
        try:
            subscribers = self.upstream_subscriber_map.get(symbol, [])
            if not subscribers:
                self.logger.info(
                    f"No subscribers remain for symbol: {symbol}. Stopping stream."
                )
                if self._should_remove_symbol(symbol):
                    await self.stream_adapter.async_remove_symbols(symbols=[symbol])
                    self.logger.info(f"Removed symbol from stream: {symbol}")
                    self._stop_data_stream_session(symbol)
                else:
                    self.logger.info(
                        f"Symbol {symbol} not in stream, nothing to remove."
                    )
            else:
                self.logger.info(
                    f"Subscribers still present for symbol: {symbol}. Stream will remain active."
                )
        except Exception as e:
            self.logger.error(f"Error stopping stream for symbol {symbol}: {e}")

    def _should_remove_symbol(self, symbol: str) -> bool:
        """Return symbols that are already in the stream."""
        current_stream_symbols = self.stream_adapter.get_stream_symbols()
        bar_symbols = set(current_stream_symbols.bars)
        quote_symbols = set(current_stream_symbols.quotes)
        should_remove_from_bar = symbol in bar_symbols
        should_remove_from_quote = symbol in quote_symbols
        return should_remove_from_bar | should_remove_from_quote

    async def async_stop(self):
        """
        Outward-facing method to gracefully shut down the market data streamer.
        Unsubscribes all subscribers, shuts down all ingest objects, stops all data stream sessions, and stops the stream adapter.
        """
        try:
            self.logger.info("Initiating full shutdown of market data streamer...")

            # Gather all subscribers and unsubscribe them
            all_subscribers = []
            for subs in self.upstream_subscriber_map.values():
                all_subscribers.extend(subs)
            unsubscribed_symbols = await self.unsubscribe(all_subscribers)
            self.logger.info(
                f"Unsubscribed all subscribers. Symbols fully unsubscribed: {unsubscribed_symbols}"
            )

            # Shutdown all ingest objects and stop any remaining data stream sessions
            for symbol, ingest_object in list(
                self.stream_data_ingest_object_map.items()
            ):
                await ingest_object.async_shutdown()
                self.logger.info(f"Shutdown stream data ingest object for {symbol}")
                self._stop_data_stream_session(symbol)

            # Stop the stream adapter
            await self.stream_adapter.async_stop_stream()
            self.logger.info("Market data streamer stopped successfully.")

            # Clear all internal state
            self.upstream_subscriber_map.clear()
            self.stream_data_ingest_object_map.clear()
            self.symbol_data_stream_session_ids.clear()

        except Exception as e:
            self.logger.error(f"Error stopping market data streamer: {e}")
