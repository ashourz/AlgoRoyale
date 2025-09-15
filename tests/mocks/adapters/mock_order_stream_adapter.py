from algo_royale.adapters.trading.order_stream_adapter import OrderStreamAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockOrderStreamAdapter(OrderStreamAdapter):
    def __init__(self):
        logger = MockLoggable()
        super().__init__(logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_order_stream(self, *args, **kwargs):
        if self.return_empty:
            return []
        return ["order_event_1", "order_event_2"]
