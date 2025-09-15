import pytest

from tests.mocks.adapters.mock_quote_adapter import MockQuoteAdapter


@pytest.fixture
def quote_adapter():
    adapter = MockQuoteAdapter()
    yield adapter


class TestQuoteAdapter:
    def test_get_quotes(self, quote_adapter):
        result = pytest.run(quote_adapter.get_quotes())
        assert result is not None
        assert isinstance(result, list)
        assert any("symbol" in q for q in result)

    def test_get_quotes_empty(self, quote_adapter):
        quote_adapter.set_return_empty(True)
        result = pytest.run(quote_adapter.get_quotes())
        assert result == []
        quote_adapter.reset_return_empty()
