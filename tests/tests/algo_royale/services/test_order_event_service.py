from datetime import datetime

import pytest

from algo_royale.models.alpaca_trading.alpaca_order import Order
from algo_royale.models.alpaca_trading.enums.order_stream_event import OrderStreamEvent
from algo_royale.models.alpaca_trading.order_stream_data import OrderStreamData
from tests.mocks.services.mock_order_event_service import MockOrderEventService


@pytest.fixture
def order_event_service():
    service = MockOrderEventService()
    yield service


@pytest.mark.asyncio
class TestOrderEventService:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, order_event_service: MockOrderEventService):
        order_event_service.reset()
        yield
        order_event_service.reset()

    async def test_async_subscribe(self, order_event_service: MockOrderEventService):
        async def sample_callback(event):
            pass

        subscriber = await order_event_service.async_subscribe(sample_callback)
        assert subscriber is not None

        async def sample_callback(event):
            pass

        with pytest.raises(Exception):
            await order_event_service.async_subscribe(sample_callback)

        order_event_service.reset_raise_exception()

    async def test_async_unsubscribe(self, order_event_service: MockOrderEventService):
        async def sample_callback(event):
            pass

        subscriber = await order_event_service.async_subscribe(sample_callback)
        # Should not raise
        await order_event_service.async_unsubscribe(subscriber)
        assert True

    async def test_start_and_stop_streaming(
        self, order_event_service: MockOrderEventService
    ):
        # _start_streaming should set _order_event_subscriber
        await order_event_service._start_streaming()
        assert order_event_service._order_event_subscriber is not None
        # _stop_streaming should clear _order_event_subscriber
        await order_event_service._stop_streaming()
        assert order_event_service._order_event_subscriber is None

    async def test_publish_order_event(
        self, order_event_service: MockOrderEventService
    ):
        # Create a fake OrderStreamData
        order = Order(
            id="order_id",
            client_order_id="client_order_id",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            submitted_at=datetime.now(),
            asset_id="asset_id",
            symbol="AAPL",
            asset_class="us_equity",
            notional=100.0,
            qty=1,
            filled_qty=0,
            order_class=None,
            order_type="market",
            type="market",
            side="buy",
            time_in_force="day",
            status="new",
            extended_hours=False,
        )
        event = OrderStreamData(
            event=OrderStreamEvent.NEW,
            price=100.0,
            timestamp=datetime.now(),
            position_qty=1,
            order=order,
        )
        # Should not raise
        await order_event_service._publish_order_event(event)
        assert True
