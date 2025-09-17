import pytest

from algo_royale.services.positions_service import PositionsService
from tests.mocks.adapters.mock_positions_adapter import MockPositionsAdapter
from tests.mocks.mock_loggable import MockLoggable
from tests.mocks.repo.mock_trade_repo import MockTradeRepo
from tests.mocks.services.mock_positions_service import MockPositionsService


@pytest.fixture
def positions_service():
    service = PositionsService(
        positions_adapter=MockPositionsAdapter(),
        trade_repo=MockTradeRepo(),
        logger=MockLoggable(),
        user_id="user_1",
        account_id="account_1",
    )
    yield service


def reset_positions_service(positions_service: MockPositionsService):
    positions_service.positions_adapter.reset()
    positions_service.trade_repo.reset()


def set_positions_service_raise_exception(
    positions_service: MockPositionsService, value: bool
):
    positions_service.positions_adapter.set_raise_exception(value)
    positions_service.trade_repo.set_raise_exception(value)


def reset_positions_service_raise_exception(positions_service: MockPositionsService):
    positions_service.positions_adapter.reset_raise_exception()
    positions_service.trade_repo.reset_raise_exception()


def set_positions_service_return_empty(
    positions_service: MockPositionsService, value: bool
):
    positions_service.positions_adapter.set_return_empty(value)
    positions_service.trade_repo.set_return_empty(value)


def reset_positions_service_return_empty(positions_service: MockPositionsService):
    positions_service.positions_adapter.reset_return_empty()
    positions_service.trade_repo.reset_return_empty()


@pytest.mark.asyncio
class TestPositionsService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, positions_service: MockPositionsService):
        print("Setup")
        reset_positions_service
        yield
        print("Teardown")
        reset_positions_service(positions_service)

    async def test_get_positions_normal(self, positions_service: MockPositionsService):
        positions = positions_service.get_positions()
        assert positions is not None

    async def test_get_positions_empty(self, positions_service: MockPositionsService):
        set_positions_service_return_empty(positions_service, True)
        positions = positions_service.get_positions()
        assert positions == [] or positions is None

    async def test_get_positions_exception(
        self, positions_service: MockPositionsService
    ):
        set_positions_service_raise_exception(positions_service, True)
        result = positions_service.get_positions()
        assert result == []

    async def test_get_positions_by_symbol_normal(
        self, positions_service: MockPositionsService
    ):
        symbol = "AAPL"
        position = positions_service.get_positions_by_symbol(symbol)
        assert position is not None

    async def test_get_positions_by_symbol_empty(
        self, positions_service: MockPositionsService
    ):
        set_positions_service_return_empty(positions_service, True)
        symbol = "AAPL"
        position = positions_service.get_positions_by_symbol(symbol)
        assert position == []

    async def test_get_positions_by_symbol_exception(
        self, positions_service: MockPositionsService
    ):
        set_positions_service_raise_exception(positions_service, True)
        symbol = "AAPL"
        result = positions_service.get_positions_by_symbol(symbol)
        assert result == []

    async def test_get_positions_by_status(
        self, positions_service: MockPositionsService
    ):
        status = "open"
        positions = positions_service.get_positions_by_status(status)
        assert positions is not None

    async def test_get_positions_by_status_exception(
        self, positions_service: MockPositionsService
    ):
        set_positions_service_raise_exception(positions_service, True)
        status = "open"
        # Using ValueError for consistency with other exception tests
        result = positions_service.get_positions_by_status(status)
        assert result == []

    async def test_get_positions_by_status_empty(
        self, positions_service: MockPositionsService
    ):
        reset_positions_service_return_empty(positions_service)
        status = "open"
        positions = positions_service.get_positions_by_status(status)
        assert positions == [] or positions is None

    async def test_sync_positions(self, positions_service: MockPositionsService):
        positions_service.sync_positions()
        assert True

    async def test_validate_positions(self, positions_service: MockPositionsService):
        await positions_service.validate_positions()
        assert True
