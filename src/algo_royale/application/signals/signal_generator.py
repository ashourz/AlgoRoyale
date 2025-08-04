import asyncio
from typing import Any

import pandas as pd

from algo_royale.application.signals.stream_data_ingest_object import (
    StreamDataIngestObject,
)
from algo_royale.application.strategies.strategy_registry import StrategyRegistry
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.backtester.strategy.signal.combined_weighted_signal_strategy import (
    CombinedWeightedSignalStrategy,
)
from algo_royale.events.async_pubsub import AsyncPubSub
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_market_data.alpaca_stream_bar import StreamBar
from algo_royale.models.alpaca_market_data.alpaca_stream_quote import StreamQuote
from algo_royale.models.alpaca_market_data.enums import DataFeed
from algo_royale.services.market_data.stream_service import StreamService


class SignalGenerator:
    def __init__(
        self,
        symbol_manager: SymbolManager,
        stream_service: StreamService,
        strategy_registry: StrategyRegistry,
        logger: Loggable,
        is_live: bool = False,
    ):
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.stream_service = stream_service
        self.strategy_registry = strategy_registry
        self.is_live = is_live
        # STREAMING
        self.latest_quote: StreamQuote = None
        self.latest_bar: StreamBar = None
        self.stream_data_ingest_object_map: dict[str, StreamDataIngestObject] = {}
        # STRATEGIES
        self.symbol_strategy_map: dict[str, CombinedWeightedSignalStrategy] = {}
        # SIGNALS
        self.pubsub_signal_map: dict[str, AsyncPubSub] = {}
        self.symbol_signal_lock_map: dict[str, asyncio.Lock] = {}
        self.symbol_pending_signal_map: dict[str, pd.DataFrame] = {}
        self.logger.info("SignalGenerator initialized.")

    async def start(self):
        """
        Generate a trading signal based on the provided data and strategy.
        """
        try:
            self.logger.info("Loading symbol strategies...")
            self._load_symbol_strategies()
            self.logger.info("Initializing stream data ingest objects...")
            self._initialize_stream_data_ingest_object()
            self.logger.info("Initializing symbol signal locks...")
            self._initialize_symbol_signal_lock()
            self.logger.info("Initializing symbol pending signal maps...")
            self._initialize_symbol_pending_signal_map()
            self.logger.info("Starting signal generation...")
            feed = DataFeed.SIP if self.is_live else DataFeed.IEX
            symbols = await self.symbol_manager.get_symbols()
            self.logger.info(
                f"Starting signal generation | feed: {feed} | symbols: {symbols}"
            )
            self.stream_service.start_stream(symbols=symbols, on_quote=self._onQuote)
        except Exception as e:
            self.logger.error(f"Error starting signal generation: {e}")

    def _load_symbol_strategies(self):
        """
        Load symbol strategies from the strategy registry.
        """
        try:
            for symbol in self.symbol_manager.get_symbols():
                self.logger.debug(f"Loading strategies for symbol: {symbol}")
                self.symbol_strategy_map[symbol] = (
                    self.strategy_registry.get_combined_weighted_signal_strategy(
                        symbol=symbol
                    )
                )

            self.logger.info("Symbol strategies loaded successfully.")
        except Exception as e:
            self.logger.error(f"Error loading symbol strategies: {e}")

    def _initialize_stream_data_ingest_object(self):
        """Initialize stream data ingest objects for each symbol."""
        for symbol in self.symbol_manager.get_symbols():
            self.stream_data_ingest_object_map[symbol] = StreamDataIngestObject(symbol)

    def _initialize_symbol_signal_lock(self):
        """
        Initialize locks for each symbol to ensure thread-safe signal generation.
        """
        for symbol in self.symbol_manager.get_symbols():
            if symbol not in self.symbol_signal_lock_map:
                self.symbol_signal_lock_map[symbol] = asyncio.Lock()
            self.logger.debug(f"Initialized lock for symbol: {symbol}")
        else:
            self.logger.debug(f"Lock already exists for symbol: {symbol}")

    def _initialize_symbol_pending_signal_map(self):
        """
        Initialize pending signal map for each symbol.
        This is used to store signals that are being processed.
        """
        for symbol in self.symbol_manager.get_symbols():
            if symbol not in self.symbol_pending_signal_map:
                self.symbol_pending_signal_map[symbol] = pd.DataFrame()
            self.logger.debug(f"Initialized pending signal map for symbol: {symbol}")
        else:
            self.logger.debug(f"Pending signal map already exists for symbol: {symbol}")

    def _onQuote(self, raw_quote: Any):
        """
        Handle incoming market quotes and generate signals.

        :param quote: The market quote data.
        """
        try:
            self.logger.debug(f"Received raw quote: {raw_quote}")
            quote = StreamQuote.from_raw(raw_quote)
            self.logger.info(f"Received quote: {quote}")
            self.stream_data_ingest_object_map[quote.symbol].async_update_with_quote(
                quote
            )
            self.logger.debug(f"Updated stream data ingest object for {quote.symbol}")

            signal = self._generate_signal(quote)
            self.logger.info(f"Generated signal: {signal}")
            # Here you would typically send the signal to a trading engine or strategy
        except Exception as e:
            self.logger.error(f"Error processing quote: {e}")

    def _onBar(self, raw_bar: Any):
        """
        Handle incoming market bars and generate signals.

        :param bar: The market bar data.
        """
        try:
            self.logger.debug(f"Received raw bar: {raw_bar}")
            bar = StreamBar.from_raw(raw_bar)
            self.logger.info(f"Received bar: {bar}")
            self.stream_data_ingest_object_map[bar.symbol].async_update_with_bar(bar)
            self.logger.debug(f"Updated stream data ingest object for {bar.symbol}")
            # Generate signal based on the bar data
            self._async_generate_signal(bar.symbol)

        except Exception as e:
            self.logger.error(f"Error processing bar: {e}")

    ##TODO: extract core logic from _async_generate_signal to a separate synchronous method
    async def _async_generate_signal(self, symbol: str):
        """
        Generate a trading signal based on the provided data and strategy.

        :param symbol: The symbol for which to generate the signal.
        :return: None if no strategy is found, otherwise publishes the generated signals.
        """
        try:
            data_ingest_object = self.stream_data_ingest_object_map.get(symbol)
            if data_ingest_object is None:
                self.logger.error(f"No data ingest object found for symbol: {symbol}")
                return
            if symbol not in self.symbol_strategy_map:
                self.logger.warning(f"No strategy found for symbol: {symbol}")
                return
            lock = self.symbol_signal_lock_map.get(symbol)
            if lock is None:
                self.logger.error(f"No lock found for symbol: {symbol}")
                return
            if lock.locked():
                self.logger.warning(f"Lock is already held for symbol: {symbol}")
                self.symbol_pending_signal_map[
                    symbol
                ] = await data_ingest_object.async_get_data()
            else:
                async with lock:
                    strategy = self.symbol_strategy_map[symbol]
                    if strategy is None:
                        self.logger.error(f"No strategy found for symbol: {symbol}")
                        return
                    # Convert data ingest object to DataFrame format expected by the strategy
                    data_df = await data_ingest_object.async_get_data()
                    self.logger.debug(f"Data for signal generation: {data_df}")
                    if data_df is None or data_df.empty:
                        self.logger.warning(f"No data available for symbol: {symbol}")
                        return
                    signals = strategy.generate_signals(data_df)
                    self.logger.debug(f"[{symbol}] Generated signals: {signals}")
                    if signals is None or signals.empty:
                        self.logger.warning(
                            f"No signals generated for symbol: {symbol}"
                        )
                        return
                    else:
                        pubsub = self.pubsub_signal_map.get(symbol)
                        if pubsub is None:
                            self.logger.error(f"No pubsub found for symbol: {symbol}")
                            return
                        pubsub.publish(signals)
                        self.logger.info(f"Published signals for {symbol} to pubsub")
        except Exception as e:
            self.logger.error(
                f"Error generating signal for {data_ingest_object.symbol}: {e}"
            )
            return

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
        except Exception as e:
            self.logger.error(f"Error stopping signal generation: {e}")
