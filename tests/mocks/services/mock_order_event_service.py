from algo_royale.services.order_event_service import OrderEventService
from tests.mocks.adapters.mock_order_stream_adapter import MockOrderStreamAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockOrderEventService(OrderEventService):
    def __init__(self):
        super().__init__(
            order_stream_adapter=MockOrderStreamAdapter(),
            logger=MockLoggable(),
        )

    def set_return_empty(self, value: bool):
        self.order_stream_adapter.set_return_empty(value)

    def reset_return_empty(self):
        self.order_stream_adapter.reset_return_empty()

    def set_raise_exception(self, value: bool):
        self.order_stream_adapter.set_raise_exception(value)

    def reset_raise_exception(self):
        self.order_stream_adapter.reset_raise_exception()

    def reset(self):
        self.reset_return_empty()
        self.reset_raise_exception()
