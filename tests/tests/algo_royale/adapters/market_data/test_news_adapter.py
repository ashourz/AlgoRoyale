import pytest

from tests.mocks.adapters.mock_news_adapter import MockNewsAdapter


@pytest.fixture
def news_adapter():
    adapter = MockNewsAdapter()
    yield adapter


class TestNewsAdapter:
    def test_get_news(self, news_adapter):
        result = pytest.run(news_adapter.get_news())
        assert result is not None
        assert isinstance(result, list)
        assert any("headline" in n for n in result)

    def test_get_news_empty(self, news_adapter):
        news_adapter.set_return_empty(True)
        result = pytest.run(news_adapter.get_news())
        assert result == []
        news_adapter.reset_return_empty()
