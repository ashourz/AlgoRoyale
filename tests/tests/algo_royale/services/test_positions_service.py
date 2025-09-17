import pytest

from tests.mocks.services.mock_positions_service import MockPositionsService


@pytest.fixture
def positions_service():
    service = MockPositionsService()
    yield service


@pytest.mark.asyncio
class TestPositionsService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, positions_service: MockPositionsService):
        print("Setup")
        positions_service.reset()
        yield
        print("Teardown")
        positions_service.reset()

    async def test_get_positions_normal(self, positions_service: MockPositionsService):
        positions = positions_service.get_positions()
        assert positions is not None

    async def test_get_positions_empty(self, positions_service: MockPositionsService):
        positions_service.set_return_empty(True)
        positions = positions_service.get_positions()
        assert positions == [] or positions is None

    async def test_get_positions_exception(
        self, positions_service: MockPositionsService
    ):
        positions_service.set_raise_exception(True)
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
        positions_service.set_return_empty(True)
        symbol = "AAPL"
        position = positions_service.get_positions_by_symbol(symbol)
        assert position == []

    async def test_get_positions_by_symbol_exception(
        self, positions_service: MockPositionsService
    ):
        positions_service.set_raise_exception(True)
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
        positions_service.set_raise_exception(True)
        status = "open"
        # Using ValueError for consistency with other exception tests
        result = positions_service.get_positions_by_status(status)
        assert result == []

    async def test_get_positions_by_status_empty(
        self, positions_service: MockPositionsService
    ):
        positions_service.set_return_empty(True)
        status = "open"
        positions = positions_service.get_positions_by_status(status)
        assert positions == [] or positions is None

    async def test_sync_positions(self, positions_service: MockPositionsService):
        positions_service.sync_positions()
        assert True

    async def test_validate_positions(self, positions_service: MockPositionsService):
        await positions_service.validate_positions()
        assert True
