import pytest

from tests.mocks.services.mock_account_cash_service import MockAccountCashService


@pytest.fixture
def account_cash_service():
    service = MockAccountCashService()
    yield service


@pytest.mark.asyncio
class TestAccountCashService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, account_cash_service: MockAccountCashService):
        print("Setup")
        account_cash_service.reset()
        yield
        print("Teardown")
        account_cash_service.reset()

    def test_total_cash(self, account_cash_service: MockAccountCashService):
        # Default should be 0
        assert account_cash_service.total_cash() == 0
        # Set and check
        account_cash_service._total_cash = 1000
        assert account_cash_service.total_cash() == 1000

    def test_buying_power(self, account_cash_service: MockAccountCashService):
        # Default should be 0
        assert account_cash_service.buying_power() == 0
        # Set and check
        account_cash_service._buying_power = 500
        assert account_cash_service.buying_power() == 500

    def test_unsettled_cash(self, account_cash_service: MockAccountCashService):
        account_cash_service._total_cash = 1000
        account_cash_service._buying_power = 700
        assert account_cash_service.unsettled_cash() == 300

    async def test_async_update_cash_info_exception(
        self, account_cash_service: MockAccountCashService
    ):
        # Mock fetch_account_data to raise
        def raise_exc():
            raise Exception("fail")

        account_cash_service.cash_adapter.fetch_account_data = raise_exc
        await account_cash_service.async_update_cash_info()
        assert account_cash_service.buying_power() == 0
        assert account_cash_service.total_cash() == 0
