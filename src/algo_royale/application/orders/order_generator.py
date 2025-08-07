import asyncio

from pandas import DataFrame

from algo_royale.application.market_data.market_data_streamer import MarketDataStreamer
from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.application.symbol.symbol_manager import SymbolManager
from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.events.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.logging.loggable import Loggable


class OrderGenerator:
    order_event_type = "ORDER_GENERATED"

    def __init__(
        self,
        symbol_manager: SymbolManager,
        market_data_streamer: MarketDataStreamer,
        signal_generator: SignalGenerator,
        logger: Loggable,
    ):
        """
        Initialize the OrderGenerator with a trading symbol and an optional logger.

        Args:
            market_data_streamer (MarketDataStreamer): The market data streamer instance.
            signal_generator (SignalGenerator): The signal generator instance.
            logger (Loggable): Logger for logging events and errors.
        """
        self.logger = logger
        self.symbol_manager = symbol_manager
        self.market_data_streamer = market_data_streamer
        self.signal_generator = signal_generator
        # MARKET DATA
        self.symbol_async_subscriber_map: dict[str, AsyncSubscriber] = {}
        # ORDERS
        self.pubsub_orders_map: dict[str, AsyncPubSub] = {}
        self.symbol_order_lock_map: dict[str, asyncio.Lock] = {}
        self.logger.info("OrderGenerator initialized.")

    async def start(self):
        """
        Start the order generation process.
        """
        try:
            symbols = await self.signal_generator.symbol_manager.async_get_symbols()
            self.logger.info("Initializing symbol order locks...")
            self._initialize_symbol_order_lock()
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_signal_streams()
            self.logger.info(f"Starting order generation | symbols: {symbols}")
            self.market_data_streamer.start_stream(
                symbols=symbols, on_quote=self._onQuote
            )
        except Exception as e:
            self.logger.error(f"Error starting order generation: {e}")

    def _initialize_symbol_order_lock(self, symbols: list[str]):
        """
        Initialize locks for each symbol to ensure thread-safe signal generation.
        """
        for symbol in symbols:
            if symbol not in self.symbol_order_lock_map:
                self.symbol_order_lock_map[symbol] = asyncio.Lock()
            self.logger.debug(f"Initialized lock for symbol: {symbol}")
        else:
            self.logger.debug(f"Lock already exists for symbol: {symbol}")

    def _subscribe_to_signal_streams(self, symbols: list[str]):
        """
        Subscribe to the signal stream for a specific symbol.
        This will allow the order generator to receive real-time data updates.
        """
        try:
            for symbol in symbols:
                self.logger.debug(f"Subscribing to stream for symbol: {symbol}")

                async_subscriber = self.signal_generator.subscribe_to_signals(
                    symbol=symbol,
                    callback=lambda data: self._async_generate_signal(
                        symbol=symbol, data=data
                    ),
                )
                self.symbol_async_subscriber_map[symbol] = async_subscriber
                self.logger.info(f"Subscribed to signal stream for symbol: {symbol}")
        except Exception as e:
            self.logger.error(f"Error subscribing to signal stream for {symbol}: {e}")

    async def _async_generate_order(self, symbol: str, signal: DataFrame):
        """
        Generate a trading order based on the provided data and strategy.

        :param symbol: The symbol for which to generate the order.
        :param signal: The trading signal DataFrame containing the order details.
        :return: None if no strategy is found, otherwise publishes the generated order.
        """
        try:
            if symbol not in self.symbol_order_lock_map:
                self.logger.warning(f"No order lock found for symbol: {symbol}")
                return

            lock = self.symbol_order_lock_map[symbol]
            async with lock:
                # generate order
                self._generate_order(symbol, signal)
        except Exception as e:
            self.logger.error(f"Error generating order for {symbol}: {e}")
            return

    def _generate_order(self, symbol: str, signal: DataFrame):
        """
        Generate a trading order based on the provided signal DataFrame.

        :param symbol: The symbol for which to generate the order.
        :param signal: The trading signal DataFrame containing the order details.
        """
        try:
            entry_signal = signal.get(
                SignalStrategyColumns.ENTRY_SIGNAL, SignalType.HOLD.value
            )
            exit_signal = signal.get(
                SignalStrategyColumns.EXIT_SIGNAL, SignalType.HOLD.value
            )
            if entry_signal == SignalType.BUY.value:
                order_type = "BUY"
            elif exit_signal == SignalType.SELL.value:
                order_type = "SELL"
            else:
                self.logger.info(
                    f"No actionable signal for {symbol}. Skipping order generation."
                )
                return
        except Exception as e:
            self.logger.error(f"Error generating order for {symbol}: {e}")
