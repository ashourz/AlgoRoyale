from algo_royale.adapters.trading.orders_adapter import OrdersAdapter
from tests.mocks.clients.alpaca.mock_alpaca_orders_client import MockAlpacaOrdersClient
from tests.mocks.mock_loggable import MockLoggable


class MockOrdersAdapter(OrdersAdapter):
    def __init__(self):
        client = MockAlpacaOrdersClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)

    def set_return_empty(self, value: bool):
        self.client.return_empty = value

    def reset_return_empty(self):
        self.client.return_empty = False

    def set_throw_exception(self, value: bool):
        self.client.throw_exception = value

    def reset_throw_exception(self):
        self.client.throw_exception = False
