from algo_royale.adapters.trading.orders_adapter import OrdersAdapter
from tests.mocks.clients.mock_alpaca_orders_client import MockAlpacaOrdersClient
from tests.mocks.mock_loggable import MockLoggable


class MockOrdersAdapter(OrdersAdapter):
    def __init__(self):
        client = MockAlpacaOrdersClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_orders(self, *args, **kwargs):
        if self.return_empty:
            return []
        return [{"id": "order1", "symbol": "AAPL"}]
