import asyncio
from typing import Any, Callable

import pandas as pd

from algo_royale.application.market_data.market_data_raw_streamer import (
    MarketDataRawStreamer,
)
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.application.signals.stream_signal_roster_object import (
    StreamSignalRosterObject,
)
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.backtester.column_names.feature_engineering_columns import (
    FeatureEngineeringColumns,
)
from algo_royale.logging.loggable import Loggable


class MarketDataEnrichedStreamer:
    signal_event_type = "DATA_ENRICHED"

    def __init__(
        self,
        symbol_manager: SymbolManager,
        market_data_streamer: MarketDataRawStreamer,
        feature_engineering_func: Callable[[pd.DataFrame], pd.DataFrame],
        logger: Loggable,
    ):
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.market_data_streamer = market_data_streamer
        self.feature_engineering_func = feature_engineering_func
        # MARKET DATA
        self.symbol_async_subscriber_map: dict[str, AsyncSubscriber] = {}
        # FEATURE ENGINEERING
        self.symbol_enrichment_lock_map: dict[str, asyncio.Lock] = {}
        self.symbol_enrichment_buffer: dict[str, pd.DataFrame] = {}
        self.enrichment_max_lookback = (
            FeatureEngineeringColumns.get_max_lookback_from_columns()
        )
        self.logger.info(
            f"MarketDataEnrichedStreamer initialized with max lookback: {self.enrichment_max_lookback}"
        )

    async def async_start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            symbols = await self.symbol_manager.async_get_symbols()
            self.logger.info("Initializing symbol signal locks...")
            self._initialize_symbol_enrichment_lock(symbols=symbols)
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_market_streams(symbols=symbols)
            self.logger.info("Creating signal roster object...")
            self.signal_roster = StreamSignalRosterObject(
                initial_symbols=symbols, logger=self.logger
            )
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

    def _initialize_symbol_enrichment_lock(self, symbols: list[str]):
        """
        Initialize locks for each symbol to ensure thread-safe access to enrichment operations.
        """
        for symbol in symbols:
            if symbol not in self.symbol_enrichment_lock_map:
                self.symbol_enrichment_lock_map[symbol] = asyncio.Lock()
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
        Generate a trading signal based on the provided data and strategy.

        :param symbol: The symbol for which to generate the signal.
        :return: None if no strategy is found, otherwise publishes the generated signals.
        """
        try:
            if symbol not in self.symbol_strategy_map:
                self.logger.warning(f"No strategy found for symbol: {symbol}")
                return

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
        self.logger.debug(f"Generating signals for {symbol} with data: {data}")
        signals = strategy.generate_signals(data)
        self.logger.debug(f"[{symbol}] Generated signals: {signals}")
        if signals is None or signals.empty:
            self.logger.warning(f"No signals generated for symbol: {symbol}")
            return
        else:
            payload = SignalDataPayload(signals=signals, price_data=data)
            await self.signal_roster.async_set_signal_data_payload(
                symbol=symbol, payload=payload
            )
            self.logger.info(
                f"Signals generated and set for symbol: {symbol}, signals: {signals}"
            )

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
        self.signal_roster.unsubscribe(subscriber=subscriber)

    def _unsubscribe_from_market_data(self):
        """
        Unsubscribe from all market data streams for all symbols.
        """
        for symbol, async_subscriber in self.symbol_async_subscriber_map.items():
            self.market_data_streamer.unsubscribe_from_stream(symbol, async_subscriber)
            self.logger.info(f"Unsubscribed from {symbol} market data stream")
        self.symbol_async_subscriber_map.clear()

    async def stop(self):
        """
        Stop the signal generation service.
        """
        try:
            self.logger.info("Stopping signal generation service...")
            await self.signal_roster.async_shutdown()
            self.logger.info("Stopping signal generation...")
            await self.market_data_streamer.async_stop()
            self.logger.info("Signal generation stopped.")
            self.symbol_strategy_map.clear()
            self.logger.info("Symbol strategy map cleared.")
            self._unsubscribe_from_market_data()
            self.logger.info("Unsubscribed from all market data streams.")
        except Exception as e:
            self.logger.error(f"Error stopping signal generation: {e}")
