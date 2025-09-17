import pytest

from tests.mocks.services.mock_positions_service import MockPositionsService


@pytest.fixture
def positions_service():
    service = MockPositionsService()
    yield service


@pytest.mark.asyncio
class TestPositionsService:
    async def test_get_positions_normal(self, positions_service):
        positions = positions_service.get_positions()
        assert positions is not None

    async def test_get_positions_empty(self, positions_service):
        positions_service.set_return_empty(True)
        positions = positions_service.get_positions()
        assert positions == [] or positions is None
        positions_service.reset_return_empty()

    async def test_get_positions_exception(self, positions_service):
        positions_service.set_raise_exception(True)
        with pytest.raises(ValueError):
            positions_service.get_positions()
        positions_service.reset_raise_exception()
