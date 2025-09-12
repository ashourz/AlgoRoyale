from datetime import datetime
from typing import Optional

from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import (
    AlpacaOrdersClient,
)
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_order import (
    DeleteOrdersResponse,
    Order,
    OrderListResponse,
    StopLoss,
    TakeProfit,
)
from algo_royale.models.alpaca_trading.enums import (
    OrderClass,
    OrderSide,
    OrderStatusFilter,
    OrderType,
    PositionIntent,
    SortDirection,
    TimeInForce,
)


class OrdersAdapter:
    """
    Service class to interact with Alpaca's API for orders management.

    This class provides a simplified interface for interacting with Alpaca's orders API and includes
    methods for creating, retrieving, updating, and deleting orders. The parameters for each method are
    fully documented to facilitate interaction with the Alpaca platform.
    """

    def __init__(self, client: AlpacaOrdersClient, logger: Loggable):
        self.client = client
        self.logger = logger

    async def create_order(
        self,
        symbol: Optional[str] = None,
        qty: Optional[float] = None,
        notional: Optional[float] = None,
        side: Optional[OrderSide] = None,
        order_type: Optional[OrderType] = None,
        time_in_force: Optional[TimeInForce] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        trail_percent: Optional[float] = None,
        extended_hours: Optional[bool] = None,
        client_order_id: Optional[str] = None,
        order_class: Optional[OrderClass] = None,
        take_profit: Optional[TakeProfit] = None,
        stop_loss: Optional[StopLoss] = None,
        position_intent: Optional[PositionIntent] = None,
    ) -> Optional[Order]:
        """
        Create an order with the specified parameters.

        Parameters:
            - symbol (str): Symbol or currency pair (e.g., 'AAPL').
            - qty (float): Number of shares to trade.
            - notional (float): Dollar amount to trade. Cannot be used with qty.
            - side (OrderSide): 'buy' or 'sell'.
            - order_type (OrderType): Type of order (e.g., market, limit, stop).
            - time_in_force (TimeInForce): Time duration for the order (e.g., day, gtc).
            - limit_price (float): Price for limit and stop-limit orders.
            - stop_price (float): Price for stop orders.
            - trail_price (float): Price for trailing stop orders.
            - trail_percent (float): Percentage for trailing stop orders.
            - extended_hours (bool): Whether the order is eligible for premarket/after-hours trading.
            - client_order_id (str): Optional unique identifier for the order.
            - order_class (OrderClass): The order class (e.g., simple, oco, bracket).
            - take_profit (TakeProfit): Optional object for take-profit orders.
            - stop_loss (StopLoss): Optional object for stop-loss orders.
            - position_intent (PositionIntent): Strategy for options orders.

        Returns:
            - Order: The created order object.
        """
        return await self.client.create_order(
            symbol=symbol,
            qty=qty,
            notional=notional,
            side=side,
            order_type=order_type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_price=trail_price,
            trail_percent=trail_percent,
            extended_hours=extended_hours,
            client_order_id=client_order_id,
            order_class=order_class,
            take_profit=take_profit,
            stop_loss=stop_loss,
            position_intent=position_intent,
        )

    async def get_all_orders(
        self,
        status: Optional[OrderStatusFilter] = None,
        limit: Optional[int] = None,
        after: Optional[datetime] = None,
        until: Optional[datetime] = None,
        direction: Optional[SortDirection] = None,
        nested: Optional[bool] = None,
        symbols: Optional[list[str]] = None,
        side: Optional[OrderSide] = None,
    ) -> Optional[OrderListResponse]:
        """
        Retrieve all orders based on various filters.

        Parameters:
            - status (OrderStatusFilter): Order status filter (open, closed, or all).
            - limit (int): Max number of orders to return (max 500).
            - after (datetime): Only orders placed after this date-time.
            - until (datetime): Only orders placed before this date-time.
            - direction (SortDirection): Order of response (asc or desc).
            - nested (bool): Whether to include multi-leg orders.
            - symbols (list[str]): A list of symbols to filter by.
            - side (OrderSide): Side of the order ('buy' or 'sell').

        Returns:
            - OrderListResponse: The list of orders matching the filter.
        """
        return await self.client.get_all_orders(
            status=status,
            limit=limit,
            after=after,
            until=until,
            direction=direction,
            nested=nested,
            symbols=symbols,
            side=side,
        )

    async def get_order_by_client_order_id(
        self, client_order_id: str, nested: Optional[bool] = None
    ) -> Optional[Order]:
        """
        Retrieve a specific order by its client-order ID.

        Parameters:
            - client_order_id (str): The client-assigned order ID.
            - nested (bool): Whether to include multi-leg orders.

        Returns:
            - Order: The order object associated with the client-order ID.
        """
        return await self.client.get_order_by_client_order_id(
            client_order_id=client_order_id, nested=nested
        )

    async def replace_order_by_client_order_id(
        self,
        client_order_id: str,
        qty: Optional[int] = None,
        time_in_force: Optional[TimeInForce] = None,
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        new_client_order_id: Optional[str] = None,
    ) -> Optional[Order]:
        """
        Replace an existing order by its client-order ID.

        Parameters:
            - client_order_id (str): The existing order's client order ID.
            - qty (float): Number of shares to trade.
            - time_in_force (TimeInForce): Time-in-force for the order.
            - limit_price (float): Price for limit and stop-limit orders.
            - stop_price (float): Price for stop orders.
            - trail_price (float): Price for trailing stop orders.
            - new_client_order_id (str): Optional new client-side ID for the order.

        Returns:
            - Order: The updated order object.
        """
        return await self.client.replace_order_by_client_order_id(
            client_order_id=client_order_id,
            qty=qty,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_price=trail_price,
            new_client_order_id=new_client_order_id,
        )

    async def delete_order_by_client_order_id(self, client_order_id: str):
        """
        Delete an order by its client-order ID.

        Parameters:
            - client_order_id (str): The client-assigned order ID.

        Returns:
            - None: If the order was successfully deleted.
            - Raises ValueError: If the order status is not cancelable.
        """
        await self.client.delete_order_by_client_order_id(client_order_id)

    async def delete_all_orders(self) -> Optional[DeleteOrdersResponse]:
        """
        Delete all orders for the account.

        Returns:
            - DeleteOrdersResponse: The response indicating success or failure.
        """
        return await self.client.delete_all_orders()
