from algo_royale.adapters.market_data.quote_adapter import QuoteAdapter
from tests.mocks.clients.alpaca.mock_alpaca_stock_client import MockAlpacaStockClient
from tests.mocks.mock_loggable import MockLoggable


class MockQuoteAdapter(QuoteAdapter):
    def __init__(self):
        logger = MockLoggable()
        client = MockAlpacaStockClient()
        super().__init__(alpaca_stock_client=client, logger=logger)
        self.should_raise = False
        self.should_return_none = False
        self.return_value = {"mock": True}
        self.should_return_empty = False

    def set_raise(self, value: bool):
        self.should_raise = value

    def set_return_empty(self, value: bool):
        self.should_return_empty = value

    def set_return_none(self, value: bool):
        self.should_return_none = value

    def set_return_value(self, value):
        self.return_value = value

    def get_quotes(self, *args, **kwargs):
        if self.should_return_empty:
            return []
        if self.should_raise:
            raise RuntimeError("Mocked exception in get_quotes")
        if self.should_return_none:
            return None
        return self.return_value
