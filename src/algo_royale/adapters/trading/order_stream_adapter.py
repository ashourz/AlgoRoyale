from algo_royale.application.utils.async_pubsub import AsyncPubSub
from algo_royale.clients.alpaca.alpaca_trading.alpaca_order_stream_client import (
    AlpacaOrderStreamClient,
)
from algo_royale.logging.loggable import Loggable


class OrderStreamAdapter:
    """
    Adapter for handling order streams in the trading system.
    This class is responsible for processing incoming order streams
    and converting them into a format suitable for the trading engine.
    """

    def __init__(self, order_stream_client: AlpacaOrderStreamClient, logger: Loggable):
        """Initialize the OrderStreamAdapter.

        Args:
            order_stream_client (AlpacaOrderStreamClient): The order stream client to use.
            logger (Loggable): Logger instance for logging.
        """
        self.order_stream_client = order_stream_client
        self.logger = logger
        self.pubsub = AsyncPubSub()
        self.pubsubEventType = "ORDER_STREAM_EVENT"

    async def start(self, on_order_update: callable):
        """
        Start the order stream and set the callback for order updates.

        Args:
            on_order_update (callable): Coroutine function to handle order updates.
        """
        self.logger.info("Starting Order Stream...")
        await self.start_stop_pubsub.publish(
            self.pubsubEventType, self._on_start_stream, on_order_update
        )

    async def start_stream(self, on_order_update):
        """
        Start the order stream and set the callback for order updates.

        Args:
            on_order_update (callable): Coroutine function to handle order updates.
        """
        await self.order_stream_client.stream(on_order_update=on_order_update)

    async def stop_stream(self):
        """
        Stop the order stream.
        """
        await self.order_stream_client.stop()
