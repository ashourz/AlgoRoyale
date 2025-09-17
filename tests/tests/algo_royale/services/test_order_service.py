import pytest

from tests.mocks.services.mock_order_service import MockOrderService


@pytest.fixture
def order_service():
    service = MockOrderService()
    yield service


@pytest.mark.asyncio
class TestOrderService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, order_service: MockOrderService):
        print("Setup")
        order_service.reset()
        yield
        print("Teardown")
        order_service.reset()

    async def test_place_order_normal(self, order_service: MockOrderService):
        order_id = order_service.place_order("AAPL", 10, "buy")
        assert order_id is not None

    async def test_place_order_exception(self, order_service: MockOrderService):
        order_service.set_raise_exception(True)
        with pytest.raises(ValueError):
            order_service.place_order("AAPL", 10, "buy")
        order_service.reset_raise_exception()
