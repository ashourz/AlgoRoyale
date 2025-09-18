from algo_royale.application.utils.async_pubsub import AsyncSubscriber
from algo_royale.services.order_event_service import OrderEventService
from tests.mocks.adapters.mock_order_stream_adapter import MockOrderStreamAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockOrderEventService(OrderEventService):
    def __init__(self):
        super().__init__(
            order_stream_adapter=MockOrderStreamAdapter(),
            logger=MockLoggable(),
        )
        self.return_empty = False
        self.raise_exception = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    def set_raise_exception(self, value: bool):
        self.raise_exception = value

    def reset_raise_exception(self):
        self.raise_exception = False

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()

    async def async_subscribe(self, callback) -> AsyncSubscriber | None:
        if self.raise_exception:
            raise Exception("Mock exception in async_subscribe")
        if self.return_empty:
            return
        return AsyncSubscriber(
            event_type="order_event",
            callback=callback,
        )

    async def async_unsubscribe(self, subscriber: AsyncSubscriber):
        if self.raise_exception:
            raise Exception("Mock exception in async_unsubscribe")
        if self.return_empty:
            return
        return
