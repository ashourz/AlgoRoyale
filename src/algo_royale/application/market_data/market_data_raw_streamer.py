from typing import Any
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
        self.stream_subscribers: dict[str, list[AsyncSubscriber]] = {}
        self.symbol_data_stream_session_ids: dict[str, UUID] = {}
        self.logger = logger
        self.is_live = is_live
        self.clock_provider = clock_provider

    async def async_subscribe_to_stream(
        self, symbols: list[str], callback: Any
    ) -> dict[str, AsyncSubscriber]:
        """
        Subscribe to the stream for specific symbols.
        This will allow the signal generator to receive real-time data updates.

        :param symbols: The stock symbols to subscribe to.
        :param callback: The callback function to handle incoming data.
        """
        try:
            await self._async_start(symbols=symbols)
            subscriber_dict = {}
            for symbol in symbols:
                if symbol in self.stream_data_ingest_object_map:
                    subscriber = self.stream_data_ingest_object_map[symbol].subscribe(
                        callback=callback,
                    )
                    if symbol not in self.stream_subscribers:
                        self.stream_subscribers[symbol] = []
                    self.stream_subscribers[symbol].append(subscriber)
                    self.logger.info(f"Subscribed to stream for symbol: {symbol}")
                    subscriber_dict[symbol] = subscriber
                else:
                    self.logger.error(
                        f"Symbol {symbol} not found in stream data ingest objects."
                    )
            self.logger.info(f"Subscription complete for symbols: {symbols}")
            return subscriber_dict
        except Exception as e:
            self.logger.error(f"Error subscribing to stream for {symbol}: {e}")
        return {}

    async def async_unsubscribe_from_stream(
        self, symbol_subscribers: dict[str, list[AsyncSubscriber]]
    ):
        """
        Unsubscribe from the stream for specific symbols.
        This will stop the signal generator from receiving real-time data updates.
        :param symbol_subscribers: A dictionary mapping symbols to their respective subscribers to unsubscribe.
        """
        try:
            symbols_to_stop = []
            for symbol, subscribers in symbol_subscribers.items():
                if symbol in self.stream_data_ingest_object_map:
                    for subscriber in subscribers:
                        self.stream_data_ingest_object_map[symbol].unsubscribe(
                            subscriber
                        )
                        self._remove_subscriber(symbol, subscriber)

                    else:
                        self.logger.error("Subscriber is None, cannot unsubscribe.")
                if not self.stream_subscribers.get(symbol, []):
                    symbols_to_stop.append(symbol)
                self.logger.info(f"Unsubscribed from stream for symbol: {symbol}")

            await self._async_stop_streaming_symbols(symbols=symbols_to_stop)
            if not any(self.stream_subscribers.values()):
                await self._async_stop()
        except Exception as e:
            self.logger.error(f"Error unsubscribing from stream for {symbol}: {e}")

    def _start_data_stream_session(self, symbol: str) -> UUID:
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
            raise

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

    def _remove_subscriber(self, symbol: str, subscriber: AsyncSubscriber):
        """Remove a subscriber from the specified symbol's subscriber list."""
        try:
            if symbol in self.stream_subscribers:
                self.stream_subscribers[symbol].remove(subscriber)
                if not self.stream_subscribers[symbol]:
                    self.stream_subscribers.pop(symbol)
        except Exception as e:
            self.logger.error(f"Error removing subscriber for {symbol}: {e}")

    async def async_restart_stream(self, symbols: list[str]):
        """
        Restart the market data stream for all subscribed symbols.
        """
        try:
            await self._async_stop()
            await self._async_start(symbols=symbols)
        except Exception as e:
            self.logger.error(f"Error restarting stream: {e}")

    def _is_stream_started(self) -> bool:
        """Check if the stream is currently started."""
        current_stream_symbols = self.stream_adapter.get_stream_symbols()
        return any(current_stream_symbols.bars) or any(current_stream_symbols.quotes)

    def _symbols_to_remove(self, symbols: list[str]) -> set[str]:
        """Return symbols that are already in the stream."""
        current_stream_symbols = self.stream_adapter.get_stream_symbols()
        bar_symbols = set(current_stream_symbols.bars)
        quote_symbols = set(current_stream_symbols.quotes)
        requested_symbols = set(symbols)
        bar_symbols_to_remove = set(requested_symbols & bar_symbols)
        quote_symbols_to_remove = set(requested_symbols & quote_symbols)
        return bar_symbols_to_remove | quote_symbols_to_remove

    def _symbols_to_add(self, symbols: list[str]) -> set[str]:
        """Return symbols that are not already in the stream."""
        current_stream_symbols = self.stream_adapter.get_stream_symbols()
        bar_symbols = set(current_stream_symbols.bars)
        quote_symbols = set(current_stream_symbols.quotes)
        requested_symbols = set(symbols)
        bar_symbols_to_add = set(requested_symbols - bar_symbols)
        quote_symbols_to_add = set(requested_symbols - quote_symbols)
        return bar_symbols_to_add | quote_symbols_to_add

    async def _async_start(self, symbols: list[str]):
        """
        Start the market data streamer and initialize stream data ingest objects.
        """
        try:
            self._initialize_stream_data_ingest_object(symbols=symbols)
            self.logger.info("Starting signal generation...")
            if self._is_stream_started():
                symbols_to_add = self._symbols_to_add(symbols)
                if symbols_to_add:
                    await self.stream_adapter.async_add_symbols(
                        quotes=symbols_to_add, bars=symbols_to_add
                    )
                    self.logger.info(f"Added symbols to stream: {symbols_to_add}")
            else:
                feed = DataFeed.SIP if self.is_live else DataFeed.IEX
                await self.stream_adapter.async_start_stream(
                    symbols=symbols,
                    feed=feed,
                    on_quote=self._onQuote,
                    on_bar=self._onBar,
                )
                self.logger.info(f"Started stream for symbols: {symbols}")
            if symbols_to_add:
                for symbol in symbols_to_add:
                    self._start_data_stream_session(symbol)
                    self.logger.info(
                        f"Started data stream session for symbol: {symbol}"
                    )
            else:
                for symbol in symbols:
                    self._start_data_stream_session(symbol)
                    self.logger.info(
                        f"Started data stream session for symbol: {symbol}"
                    )
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

    async def _async_stop_streaming_symbols(self, symbols: list[str]):
        """
        Stop the market data stream for the specified symbols.
        """
        try:
            self.logger.info(f"Stopping stream for symbols: {symbols}")
            symbols_to_remove = self._symbols_to_remove(symbols)
            if symbols_to_remove:
                await self.stream_adapter.async_remove_symbols(
                    symbols=symbols_to_remove
                )
                self.logger.info(f"Removed symbols from stream: {symbols_to_remove}")
            for symbol in symbols_to_remove:
                self._stop_data_stream_session(symbol)
        except Exception as e:
            self.logger.error(f"Error stopping stream for symbols {symbols}: {e}")

    def _initialize_stream_data_ingest_object(self, symbols: list[str]):
        """Initialize stream data ingest objects for each symbol."""
        try:
            for symbol in symbols:
                self.logger.debug(
                    f"Initializing StreamDataIngestObject for symbol: {symbol}"
                )
                self.stream_data_ingest_object_map[symbol] = StreamDataIngestObject(
                    symbol
                )
        except Exception as e:
            self.logger.error(f"Error initializing stream data ingest objects: {e}")

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

    async def _async_unsubscribe_all_subscribers(self):
        """
        Unsubscribe all subscribers from their respective streams.
        """
        try:
            self.logger.info("Unsubscribing all subscribers from streams...")
            for symbol, subscriber in self.stream_subscribers.items():
                if symbol in self.stream_data_ingest_object_map and subscriber:
                    self.stream_data_ingest_object_map[symbol].unsubscribe(subscriber)
                    self.logger.info(f"Unsubscribed from stream for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error unsubscribing all subscribers: {e}")
        finally:
            self.stream_subscribers.clear()
            self.stream_data_ingest_object_map.clear()

    async def _async_stop(self):
        """
        Stop the market data streamer and clean up resources.
        """
        try:
            await self._async_unsubscribe_all_subscribers()
            self.logger.info("Stopping market data streamer...")
            for symbol, ingest_object in self.stream_data_ingest_object_map.items():
                await ingest_object.async_shutdown()
                self.logger.info(f"Shutdown stream data ingest object for {symbol}")
                self._stop_data_stream_session(symbol)
            await self.stream_adapter.async_stop_stream()
            self.logger.info("Market data streamer stopped successfully.")
        except Exception as e:
            self.logger.error(f"Error stopping market data streamer: {e}")
