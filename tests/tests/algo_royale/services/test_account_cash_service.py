import pytest

from algo_royale.services.account_cash_service import AccountCashService
from tests.mocks.adapters.mock_account_cash_adapter import MockAccountCashAdapter
from tests.mocks.mock_loggable import MockLoggable


@pytest.fixture
def account_cash_service():
    service = AccountCashService(
        cash_adapter=MockAccountCashAdapter(),
        logger=MockLoggable(),
    )
    yield service


def set_account_cash_service_raise_exception(
    account_cash_service: AccountCashService, value: bool
):
    account_cash_service.cash_adapter.set_raise_exception(value)


def reset_account_cash_service_raise_exception(
    account_cash_service: AccountCashService,
):
    account_cash_service.cash_adapter.reset_raise_exception()


def reset_account_cash_service(account_cash_service: AccountCashService):
    reset_account_cash_service_raise_exception(account_cash_service)


@pytest.mark.asyncio
class TestAccountCashService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, account_cash_service: AccountCashService):
        print("Setup")
        reset_account_cash_service(account_cash_service)
        yield
        print("Teardown")
        reset_account_cash_service(account_cash_service)

    def test_total_cash(self, account_cash_service: AccountCashService):
        # Default should be 0
        assert account_cash_service.total_cash() == 0
        # Set and check
        account_cash_service._total_cash = 1000
        assert account_cash_service.total_cash() == 1000

    def test_buying_power(self, account_cash_service: AccountCashService):
        # Default should be 0
        assert account_cash_service.buying_power() == 0
        # Set and check
        account_cash_service._buying_power = 500
        assert account_cash_service.buying_power() == 500

    def test_unsettled_cash(self, account_cash_service: AccountCashService):
        account_cash_service._total_cash = 1000
        account_cash_service._buying_power = 700
        assert account_cash_service.unsettled_cash() == 300

    async def test_async_update_cash_info_exception(
        self, account_cash_service: AccountCashService
    ):
        set_account_cash_service_raise_exception(account_cash_service, True)
        await account_cash_service.async_update_cash_info()
        assert account_cash_service.buying_power() == 0
        assert account_cash_service.total_cash() == 0
