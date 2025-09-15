from algo_royale.adapters.market_data.news_adapter import NewsAdapter
from tests.mocks.mock_loggable import MockLoggable


class MockNewsAdapter(NewsAdapter):
    def __init__(self):
        logger = MockLoggable()
        super().__init__(logger=logger)
        self.return_empty = False

    def set_return_empty(self, value: bool):
        self.return_empty = value

    def reset_return_empty(self):
        self.return_empty = False

    async def get_news(self, *args, **kwargs):
        if self.return_empty:
            return []
        return [{"headline": "Test News", "symbol": "AAPL"}]
