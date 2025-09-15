import pytest

from tests.mocks.adapters.mock_account_adapter import MockAccountAdapter


@pytest.fixture
def account_adapter():
    adapter = MockAccountAdapter()
    yield adapter


class TestAccountAdapter:
    def test_get_account(self, account_adapter):
        result = pytest.run(account_adapter.get_account())
        assert result is not None
        assert "id" in result

    def test_get_account_empty(self, account_adapter):
        account_adapter.set_return_empty(True)
        result = pytest.run(account_adapter.get_account())
        assert result is None
        account_adapter.reset_return_empty()
