import asyncio
from typing import Any, Callable

import pandas as pd

from algo_royale.application.market_data.market_data_raw_streamer import (
    MarketDataRawStreamer,
)
from algo_royale.application.market_data.queued_async_enriched_data_buffer import (
    QueuedAsyncEnrichedDataBuffer,
)
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer
from algo_royale.logging.loggable import Loggable


class MarketDataEnrichedStreamer:
    enrichment_event_type = "DATA_ENRICHED"

    def __init__(
        self,
        symbol_manager: SymbolManager,
        feature_engineer: FeatureEngineer,
        market_data_streamer: MarketDataRawStreamer,
        logger: Loggable,
    ):
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.market_data_streamer = market_data_streamer
        # MARKET DATA
        self.symbol_async_subscriber_map: dict[str, AsyncSubscriber] = {}
        # FEATURE ENGINEERING
        self.feature_engineer = feature_engineer
        self.symbol_enrichment_lock_map: dict[str, asyncio.Lock] = {}
        self.symbol_enrichment_buffer: dict[str, QueuedAsyncEnrichedDataBuffer] = {}
        self.pubsub_enriched_data_map: dict[str, AsyncPubSub] = {}

    async def async_start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            symbols = await self.symbol_manager.async_get_symbols()
            self.logger.info("Initializing symbol signal locks...")
            self._initialize_symbol_enrichment_lock(symbols=symbols)
            self.logger.info("Creating enrichment buffers...")
            self._create_enrichment_buffers(symbols=symbols)
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_market_streams(symbols=symbols)
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

    def _initialize_symbol_enrichment_lock(self, symbols: list[str]):
        """
        Initialize locks for each symbol to ensure thread-safe access to enrichment operations.
        """
        try:
            for symbol in symbols:
                if symbol not in self.symbol_enrichment_lock_map:
                    self.symbol_enrichment_lock_map[symbol] = asyncio.Lock()
                self.logger.debug(f"Initialized lock for symbol: {symbol}")
            else:
                self.logger.debug(f"Lock already exists for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error initializing symbol enrichment locks: {e}")

    def _create_enrichment_buffers(self, symbols: list[str]):
        """
        Create enrichment buffers for each symbol.
        """
        try:
            for symbol in symbols:
                if symbol not in self.symbol_enrichment_buffer:
                    self.symbol_enrichment_buffer[symbol] = (
                        QueuedAsyncEnrichedDataBuffer(
                            symbol=symbol,
                            feature_engineer=self.feature_engineer,
                            logger=self.logger,
                        )
                    )
                self.logger.debug(f"Initialized enrichment buffer for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error creating enrichment buffers: {e}")

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
                    callback=lambda data, symbol=symbol: self._async_data_enrichment(
                        symbol=symbol, data=data
                    ),
                )
                self.symbol_async_subscriber_map[symbol] = async_subscriber
                self.logger.info(f"Subscribed to market stream for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error subscribing to market stream for {symbol}: {e}")

    async def _async_data_enrichment(self, symbol: str, data: dict):
        """
        Enrich market data for a specific symbol.
        """
        try:
            self.logger.debug(f"Received data for {symbol}: {data}")
            lock = self.symbol_enrichment_lock_map.get(symbol)
            if lock is None:
                self.logger.error(f"No lock found for symbol: {symbol}")
                return

            async with lock:
                # Enrich data
                await self._async_data_enrichment_inner(symbol, data)
        except Exception as e:
            self.logger.error(f"Error generating signal for {symbol}: {e}")
            return

    async def _async_data_enrichment_inner(self, symbol: str, data: dict):
        """
        Inner method to handle data enrichment for a specific symbol.
        This method is called within a lock to ensure thread safety.
        """
        try:
            self.logger.debug(f"Enriching data for symbol: {symbol}")
            buffer = self.symbol_enrichment_buffer[symbol]
            if not buffer:
                self.logger.error(f"No buffer found for {symbol}")
                return
            await buffer.async_update(pd.Series(data))
            enriched_data = await buffer.async_get_latest_enriched_data()
            if enriched_data is None:
                self.logger.error(f"No enriched data found for {symbol}")
                return

            # Publish the enriched data
            await self._async_publish_enriched_data(symbol, enriched_data)
            self.logger.info(f"Enriched data published for {symbol}")
        except Exception as e:
            self.logger.error(f"Error enriching data for {symbol}: {e}")

    def _get_enriched_data_pubsub(self, symbol: str) -> AsyncPubSub:
        """
        Get the pubsub instance for the specified symbol.
        If it does not exist, create a new one.
        """
        if symbol not in self.pubsub_enriched_data_map:
            self.pubsub_enriched_data_map[symbol] = AsyncPubSub(
                event_type=self.enrichment_event_type,
                logger=self.logger,
            )
        return self.pubsub_enriched_data_map[symbol]

    async def _async_publish_enriched_data(self, symbol: str, enriched_data: pd.Series):
        """
        Publish the enriched data for a specific symbol.
        """
        try:
            pubsub = self._get_enriched_data_pubsub(symbol)
            dict_data = enriched_data.to_dict()
            await pubsub.async_publish(self.enrichment_event_type, dict_data)
            self.logger.info(f"Published enriched data for {symbol}")
        except Exception as e:
            self.logger.error(f"Error publishing enriched data for {symbol}: {e}")

    def subscribe_to_enriched_data(
        self,
        symbol: str,
        callback: Callable[[pd.Series, type], Any],
        queue_size=1,
    ) -> AsyncSubscriber:
        """
        Subscribe to enriched data for a specific symbol.

        :param symbol: The symbol to subscribe to.
        :param callback: The callback function to call with the enriched data.
        :param queue_size: The size of the queue for the subscriber.
        """
        pubsub = self._get_enriched_data_pubsub(symbol)
        return pubsub.subscribe(
            callback=callback,
            queue_size=queue_size,
        )

    def unsubscribe_from_enriched_data(self, symbol: str, subscriber: AsyncSubscriber):
        """
        Unsubscribe from enriched data for a specific subscriber.

        :param subscriber: The subscriber to unsubscribe from.
        """
        try:
            pubsub = self._get_enriched_data_pubsub(symbol)
            pubsub.unsubscribe(subscriber=subscriber)
        except Exception as e:
            self.logger.error(
                f"Error unsubscribing from enriched data for {symbol}: {e}"
            )

    def _unsubscribe_from_market_data(self):
        """
        Unsubscribe from all market data streams for all symbols.
        """
        try:
            for symbol, async_subscriber in self.symbol_async_subscriber_map.items():
                self.market_data_streamer.unsubscribe_from_stream(
                    symbol, async_subscriber
                )
                self.logger.info(f"Unsubscribed from {symbol} market data stream")
        except Exception as e:
            self.logger.error(f"Error unsubscribing from market data streams: {e}")
        self.symbol_async_subscriber_map.clear()

    async def async_stop(self):
        """
        Stop the enriched data generation service.
        """
        try:
            self._unsubscribe_from_market_data()
            self.logger.info("Unsubscribed from all market data streams.")
        except Exception as e:
            self.logger.error(f"Error stopping enriched data generation: {e}")
