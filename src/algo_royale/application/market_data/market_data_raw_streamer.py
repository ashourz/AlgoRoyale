from logging import Logger
from typing import Any

from algo_royale.adapters.market_data.stream_adapter import StreamAdapter
from algo_royale.application.signals.stream_data_ingest_object import (
    StreamDataIngestObject,
)
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.models.alpaca_market_data.alpaca_stream_bar import StreamBar
from algo_royale.models.alpaca_market_data.alpaca_stream_quote import StreamQuote
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.symbol_service import SymbolService


class MarketDataRawStreamer:
    """
    MarketDataStreamer is responsible for managing the streaming of market data
    for various stock symbols. It initializes stream data ingest objects for each
    symbol and subscribes to the relevant market data feeds.
    """

    def __init__(
        self,
        symbol_manager: SymbolService,
        stream_service: StreamAdapter,
        logger: Logger,
        is_live: bool = False,
    ):
        self.symbol_manager = symbol_manager
        self.stream_service = stream_service
        self.stream_data_ingest_object_map: dict[str, StreamDataIngestObject] = {}
        self.stream_subscribers: dict[str, AsyncSubscriber] = {}
        self.logger = logger
        self.is_live = is_live

    async def async_subscribe_to_stream(
        self, symbol: str, callback: Any
    ) -> AsyncSubscriber | None:
        """
        Subscribe to the stream for a specific symbol.
        This will allow the signal generator to receive real-time data updates.

        :param symbol: The stock symbol to subscribe to.
        :param callback: The callback function to handle incoming data.
        """
        try:
            if not any(self.stream_subscribers.values()):
                # No subscribers present, need to run async_start
                await self._async_start()
            if symbol in self.stream_data_ingest_object_map:
                subscriber = self.stream_data_ingest_object_map[symbol].subscribe(
                    callback=callback,
                )
                self.stream_subscribers[symbol] = subscriber
                self.logger.info(f"Subscribed to stream for symbol: {symbol}")
                return subscriber
            else:
                self.logger.error(
                    f"Symbol {symbol} not found in stream data ingest objects."
                )
        except Exception as e:
            self.logger.error(f"Error subscribing to stream for {symbol}: {e}")
        return None

    async def async_unsubscribe_from_stream(
        self, symbol: str, subscriber: AsyncSubscriber
    ):
        """
        Unsubscribe from the stream for a specific symbol.

        :param subscriber: The subscriber to unsubscribe.
        """
        try:
            if symbol in self.stream_data_ingest_object_map:
                if subscriber:
                    self.stream_data_ingest_object_map[symbol].unsubscribe(subscriber)
                    self.stream_subscribers.pop(symbol, None)
                    self.logger.info(f"Unsubscribed from stream for symbol: {symbol}")
                else:
                    self.logger.error("Subscriber is None, cannot unsubscribe.")
                if not any(self.stream_subscribers.values()):
                    await self._async_stop()
        except Exception as e:
            self.logger.error(f"Error unsubscribing from stream for {symbol}: {e}")

    async def async_restart_stream(self):
        """
        Restart the market data stream for all subscribed symbols.
        """
        try:
            await self._async_stop()
            await self._async_start()
        except Exception as e:
            self.logger.error(f"Error restarting stream: {e}")

    async def _async_start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            symbols = await self.symbol_manager.async_get_symbols()
            self.logger.info("Initializing stream data ingest objects...")
            self._initialize_stream_data_ingest_object()
            self.logger.info("Initializing symbol signal locks...")
            self._initialize_symbol_signal_lock()
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_streams()
            self.logger.info("Starting signal generation...")
            feed = DataFeed.SIP if self.is_live else DataFeed.IEX
            self.logger.info(f"Starting streaming | feed: {feed} | symbols: {symbols}")
            self.stream_service.start_stream(
                symbols=symbols, feed=feed, on_quote=self._onQuote, on_bar=self._onBar
            )
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

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
            self.stream_service.stop_stream()
            self.logger.info("Market data streamer stopped successfully.")
        except Exception as e:
            self.logger.error(f"Error stopping market data streamer: {e}")
