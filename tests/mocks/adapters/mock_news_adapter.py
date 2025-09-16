from algo_royale.adapters.market_data.news_adapter import NewsAdapter
from tests.mocks.clients.mock_alpaca_news_client import MockAlpacaNewsClient
from tests.mocks.mock_loggable import MockLoggable


class MockNewsAdapter(NewsAdapter):
    def __init__(self):
        client = MockAlpacaNewsClient()
        logger = MockLoggable()
        super().__init__(client=client, logger=logger)

    def set_return_empty(self, value: bool):
        self.client.return_empty = value

    def reset_return_empty(self):
        self.client.return_empty = False
