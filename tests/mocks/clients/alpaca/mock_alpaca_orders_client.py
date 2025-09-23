from datetime import datetime

from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import (
    AlpacaOrdersClient,
)
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


class MockAlpacaOrdersClient(AlpacaOrdersClient):
    def __init__(self):
        self.logger = MockLoggable()
        super().__init__(
            logger=self.logger,
            base_url="https://mock.alpaca.markets",
            api_key="fake_key",
            api_secret="fake_secret",
            api_key_header="APCA-API-KEY-ID",
            api_secret_header="APCA-API-SECRET-KEY",
            http_timeout=5,
            reconnect_delay=1,
            keep_alive_timeout=5,
        )
        self.return_empty = False
        self.raise_exception = False

    async def create_order(
        self,
        symbol,
        qty=None,
        notional=None,
        side=None,
        order_type=None,
        time_in_force=None,
        limit_price=None,
        stop_price=None,
        trail_price=None,
        trail_percent=None,
        extended_hours=None,
        client_order_id=None,
        order_class=None,
        take_profit=None,
        stop_loss=None,
        position_intent=None,
        **kwargs,
    ):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaOrdersClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
        # Use valid enum defaults if None is passed
        side = side or OrderSide.BUY
        order_type = order_type or OrderType.MARKET
        time_in_force = time_in_force or TimeInForce.DAY
        # Use provided client_order_id if available, else default
        coid = client_order_id or kwargs.get("client_order_id") or "client_order_id"
        return Order(
            symbol=symbol,
            qty=qty if qty is not None else 1,
            side=side,
            type=order_type,
            time_in_force=time_in_force,
            id="order_id",
            status="new",
            client_order_id=coid,
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
        self,
        status=OrderStatusFilter.OPEN,
        limit=10,
        direction=SortDirection.DESC,
        **kwargs,
    ):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaOrdersClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return OrderListResponse(orders=[])
        fake_order = await self.create_order(
            symbol="AAPL",
            qty=1,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
        )
        return OrderListResponse(orders=[fake_order])

    async def get_order_by_client_order_id(self, client_order_id, **kwargs):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaOrdersClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
        return await self.create_order(
            symbol="AAPL",
            qty=1,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
        )

    async def replace_order_by_client_order_id(
        self,
        client_order_id,
        qty=None,
        time_in_force=None,
        limit_price=None,
        stop_price=None,
        trail_price=None,
        new_client_order_id=None,
        **kwargs,
    ):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaOrdersClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
        return await self.create_order(
            symbol="AAPL",
            qty=qty or 1,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            time_in_force=TimeInForce.DAY,
        )

    async def delete_order_by_id(self, order_id):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaOrdersClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return None
        return DeleteOrderStatus(id=order_id, status=200)

    async def delete_all_orders(self):
        if self.raise_exception:
            raise Exception(
                "MockAlpacaOrdersClient: Exception forced by throw_exception flag."
            )
        if self.return_empty:
            return DeleteOrdersResponse(orders=[])
        return DeleteOrdersResponse(
            orders=[DeleteOrderStatus(id="order_id", status=200)]
        )

    async def aclose(self):
        pass
