from algo_royale.adapters.trading.order_stream_adapter import OrderStreamAdapter
from tests.mocks.clients.mock_alpaca_order_stream_client import (
    MockAlpacaOrderStreamClient,
)
from tests.mocks.mock_loggable import MockLoggable


class MockOrderStreamAdapter(OrderStreamAdapter):
    def __init__(self):
        client = MockAlpacaOrderStreamClient()
        logger = MockLoggable()
        super().__init__(order_stream_client=client, logger=logger)

    def set_return_empty(self, value: bool):
        self.order_stream_client.return_empty = value

    def reset_return_empty(self):
        self.order_stream_client.return_empty = False

    async def _on_start_stream(self, data=None):
        # Stub for test compatibility
        pass
