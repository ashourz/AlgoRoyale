import asyncio

from algo_royale.application.signals.signal_generator import SignalGenerator
from algo_royale.application.signals.signals_data_payload import SignalDataPayload
from algo_royale.backtester.column_names.strategy_columns import SignalStrategyColumns
from algo_royale.backtester.enums.signal_type import SignalType
from algo_royale.events.async_pubsub import AsyncPubSub
from algo_royale.logging.loggable import Loggable


class OrderGenerator:
    order_event_type = "ORDER_GENERATED"

    def __init__(
        self,
        signal_generator: SignalGenerator,
        logger: Loggable,
    ):
        """
        Initialize the OrderGenerator with a trading symbol and an optional logger.

        Args:
            signal_generator (SignalGenerator): The signal generator instance.
            logger (Loggable): Logger for logging events and errors.
        """
        self.logger = logger
        # SIGNAL GENERATOR
        self.signal_generator = signal_generator
        # ORDERS
        self.order_lock: asyncio.Lock = asyncio.Lock()
        self.pubsub_orders_map: dict[str, AsyncPubSub] = {}
        self.logger.info("OrderGenerator initialized.")

    async def async_start(self):
        """
        Start the order generation process.
        """
        try:
            self.logger.info("Subscribing to streams...")
            self._subscribe_to_roster_stream()
            self.logger.info("Starting signal generation...")
            await self.signal_generator.async_start()
            self.logger.info("Starting order generation...")
        except Exception as e:
            self.logger.error(f"Error starting order generation: {e}")

    def _subscribe_to_roster_stream(self):
        """Subscribe to the signal roster stream to receive updates."""
        try:
            self.logger.info("Subscribing to signal roster stream...")
            async_subscriber = self.signal_generator.subscribe_to_signals(
                callback=lambda roster: self._async_generate_orders(roster=roster),
            )
            self.signal_roster_subscriber = async_subscriber
        except Exception as e:
            self.logger.error(f"Error subscribing to signal stream: {e}")

    async def _async_generate_orders(self, roster: dict[str, SignalDataPayload]):
        """
        Generate orders based on the provided signal roster.
        """
        try:
            async with self.order_lock:
                # generate order
                self._generate_orders(roster=roster)
        except Exception as e:
            self.logger.error(f"Error generating order: {e}")
            return

    ## TODO: Implement the order generation logic. Convert roster to portfolio strategy input

    def _generate_orders(self, roster: dict[str, SignalDataPayload]):
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
