from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.clients.alpaca.alpaca_trading.alpaca_order_stream_client import (
    AlpacaOrderStreamClient,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData


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

    async def start(self):
        """
        Start the order stream and set the callback for order updates.

        Args:
            on_order_update (callable): Coroutine function to handle order updates.
        """
        try:
            self.logger.info("Starting Order Stream...")
            await self._start_stream(self._on_start_stream)
        except Exception as e:
            self.logger.error(f"Failed to start Order Stream: {e}")

    async def stop(self):
        """
        Stop the order stream gracefully.
        """
        try:
            await self._stop_stream()
            self.logger.info("Order Stream stopped.")
        except Exception as e:
            self.logger.error(f"Failed to stop Order Stream: {e}")

    async def _start_stream(self, on_order_update):
        """
        Start the order stream and set the callback for order updates.

        Args:
            on_order_update (callable): Coroutine function to handle order updates.
        """
        try:
            await self.order_stream_client.stream(on_order_update=on_order_update)
        except Exception as e:
            self.logger.error(f"Error starting order stream: {e}")

    async def _stop_stream(self):
        """
        Stop the order stream.
        """
        try:
            self.logger.info("Stopping Order Stream...")
            await self.order_stream_client.stop()
        except Exception as e:
            self.logger.error(f"Failed to stop Order Stream: {e}")

    async def _on_order_update(self, data):
        """
        Callback for handling order updates from the stream.

        Args:
            data (dict): The order update data received from the stream.
        """
        try:
            self.logger.debug(f"Received order update: {data}")
            order_stream_data = OrderStreamData.from_dict(data)
            await self.pubsub.async_publish(self.pubsubEventType, order_stream_data)
        except Exception as e:
            self.logger.error(f"Error processing order update: {e}")

    def subscribe(self, callback) -> AsyncSubscriber | None:
        """
        Subscribe to order stream events.

        Args:
            callback (callable): Coroutine function to handle order stream events.
        """
        try:
            async_subscriber = self.pubsub.subscribe(self.pubsubEventType, callback)
            self.logger.info("Subscribed to order stream events.")
            return async_subscriber
        except Exception as e:
            self.logger.error(f"Failed to subscribe to order stream events: {e}")
        return None

    def unsubscribe(self, subscriber: AsyncSubscriber):
        """
        Unsubscribe from order stream events.

        Args:
            subscriber (AsyncSubscriber): The subscriber to unsubscribe.
        """
        try:
            self.pubsub.unsubscribe(subscriber)
            self.logger.info("Unsubscribed from order stream events.")
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from order stream events: {e}")
