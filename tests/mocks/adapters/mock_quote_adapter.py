from algo_royale.adapters.market_data.quote_adapter import QuoteAdapter
from tests.mocks.clients.alpaca.mock_alpaca_stock_client import MockAlpacaStockClient
from tests.mocks.mock_loggable import MockLoggable


class MockQuoteAdapter(QuoteAdapter):
    def __init__(self):
        logger = MockLoggable()
        client = MockAlpacaStockClient()
        super().__init__(alpaca_stock_client=client, logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.client.return_empty = value

    def reset_return_empty(self):
        self.client.return_empty = False
