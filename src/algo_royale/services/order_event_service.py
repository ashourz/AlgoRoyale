from logging import Logger
from typing import Callable

from algo_royale.adapters.trading.order_stream_adapter import OrderStreamAdapter
from algo_royale.application.utils.async_pubsub import AsyncPubSub, AsyncSubscriber
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData


class OrderEventService:
    event_type = "order_event"

    def __init__(self, order_stream_adapter: OrderStreamAdapter, logger: Logger):
        self.order_stream_adapter = order_stream_adapter
        self.logger = logger
        self._order_event_subscriber = None
        self._order_event_pubsub = AsyncPubSub()

    async def async_subscribe(
        self, callback: Callable[[OrderStreamData], None], queue_size: int = 0
    ) -> AsyncSubscriber:
        """Subscribe to order events."""
        if not self._order_event_subscriber:
            self.logger.warning("Order stream not started. Starting now.")
            await self._start_streaming()
        async_subscriber = self._order_event_pubsub.subscribe(
            event_type=self.event_type, callback=callback, queue_size=queue_size
        )
        return async_subscriber

    async def async_unsubscribe(self, subscriber):
        """Unsubscribe from order events."""
        self._order_event_pubsub.unsubscribe(subscriber=subscriber)
        if not self._order_event_pubsub.has_subscribers(event_type=self.event_type):
            self.logger.info("No more subscribers. Stopping order event streaming.")
            await self._stop_streaming()

    async def _start_streaming(self):
        try:
            if self._order_event_subscriber:
                self.logger.warning("Order stream already started.")
                return
            async_subscriber = self.order_stream_adapter.subscribe(
                callback=self._publish_order_event
            )
            self._order_event_subscriber = async_subscriber
        except Exception as e:
            self.logger.error(f"Error streaming order events: {e}")

    async def _stop_streaming(self):
        """Stop the order stream adapter."""
        try:
            if not self._order_event_subscriber:
                self.logger.warning("Order stream not started.")
                return True
            await self.order_stream_adapter.stop()
            self.logger.info("Order stream stopped.")
            self._order_event_subscriber = None
            return True
        except Exception as e:
            self.logger.error(f"Error stopping order stream: {e}")
            return False

    async def _publish_order_event(self, data: OrderStreamData):
        """Publish an order event to the event bus."""
        await self._order_event_pubsub.async_publish(
            event_type=self.event_type, data=data
        )
