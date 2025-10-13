import pytest

from tests.mocks.adapters.mock_news_adapter import MockNewsAdapter


@pytest.fixture
def news_adapter():
    adapter = MockNewsAdapter()
    yield adapter


@pytest.mark.asyncio
class TestNewsAdapter:
    async def test_get_recent_news(self, news_adapter):
        result = await news_adapter.get_recent_news(symbols=["AAPL"])
        assert result is not None
        assert hasattr(result, "news")
        assert isinstance(result.news, list)
        assert any(hasattr(n, "headline") for n in result.news)

    async def test_get_recent_news_empty(self, news_adapter):
        news_adapter.set_return_empty(True)
        result = await news_adapter.get_recent_news(symbols=["AAPL"])
        assert result is not None
        assert result.news == []
        news_adapter.reset_return_empty()

    async def test_get_news_in_date_range(self, news_adapter):
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        result = await news_adapter.get_news_in_date_range(
            symbols=["AAPL"], start_date=start_date, end_date=end_date
        )
        assert result is not None
        assert hasattr(result, "news")
        assert isinstance(result.news, list)
        assert all(hasattr(n, "headline") for n in result.news)

    async def test_get_news_in_date_range_empty(self, news_adapter):
        news_adapter.set_return_empty(True)
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        result = await news_adapter.get_news_in_date_range(
            symbols=["AAPL"], start_date=start_date, end_date=end_date
        )
        assert result is not None
        assert result.news == []
        news_adapter.reset_return_empty()
