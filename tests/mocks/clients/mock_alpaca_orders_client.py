from datetime import datetime

from algo_royale.models.alpaca_trading.alpaca_order import (
    DeleteOrdersResponse,
    DeleteOrderStatus,
    Order,
    OrderListResponse,
)
from algo_royale.models.alpaca_trading.enums.enums import (
    OrderSide,
    OrderStatusFilter,
    OrderType,
    SortDirection,
    TimeInForce,
)
from tests.mocks.mock_loggable import MockLoggable


class MockAlpacaOrdersClient:
    def __init__(self, logger=None, **kwargs):
        self.logger = logger or MockLoggable()

    async def create_order(
        self, symbol, qty, side, order_type, time_in_force, **kwargs
    ):
        return Order(
            symbol=symbol,
            qty=qty,
            side=side,
            type=order_type,
            time_in_force=time_in_force,
            id="order_id",
            status="new",
            client_order_id="client_order_id",
            created_at=datetime(2024, 1, 1, 9, 30),
            updated_at=datetime(2024, 1, 1, 9, 31),
            submitted_at=datetime(2024, 1, 1, 9, 30),
            asset_id="asset_id",
            asset_class="us_equity",
            filled_qty=0,
            order_type=order_type,
            extended_hours=False,
        )

    async def get_all_orders(
        self, status=OrderStatusFilter.OPEN, limit=10, direction=SortDirection.DESC
    ):
        fake_order = await self.create_order(
            symbol="AAPL",
            qty=1,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
        )
        return OrderListResponse(orders=[fake_order])

    async def get_order_by_client_order_id(self, client_order_id):
        return await self.create_order(
            symbol="AAPL",
            qty=1,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
        )

    async def delete_order_by_client_order_id(self, client_order_id):
        return DeleteOrderStatus(id=client_order_id, status=200)

    async def delete_all_orders(self):
        return DeleteOrdersResponse(
            orders=[DeleteOrderStatus(id="order_id", status=200)]
        )

    async def aclose(self):
        pass
