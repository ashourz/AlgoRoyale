from abc import ABC
from datetime import datetime

from algo_royale.clients.db.dao.order_dao import OrderDAO
from algo_royale.clients.db.dao.order_trades_dao import OrderTradesDAO
from algo_royale.clients.db.dao.position_dao import PositionDAO
from algo_royale.clients.db.dao.position_trades_dao import PositionTradesDAO
from algo_royale.clients.db.dao.trade_dao import TradeDAO
from algo_royale.logging.loggable import Loggable


class OrderStatus(ABC):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"


class OrderType(ABC):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderAction(ABC):
    BUY = "buy"
    SELL = "sell"


## TODO: Update DAO instances to repos
class OrderServices:
    def __init__(
        self,
        order_dao: OrderDAO,
        position_dao: PositionDAO,
        trade_dao: TradeDAO,
        order_trades_dao: OrderTradesDAO,
        position_trades_dao: PositionTradesDAO,
        logger: Loggable,
        user_id: str,
        account_id: str,
        days_to_settle: int = 1,
    ):
        self.dao = order_dao
        self.position_dao = position_dao
        self.trade_dao = trade_dao
        self.order_trades_dao = order_trades_dao
        self.position_trades_dao = position_trades_dao
        self.user_id = user_id
        self.account_id = account_id
        self.days_to_settle = days_to_settle
        self.logger = logger

    def fetch_orders_by_status(
        self, status: OrderStatus, limit: int = 100, offset: int = 0
    ) -> list:
        """Fetch all orders for a specific status with pagination.
        :param status: Status of the orders to fetch (e.g., 'open', 'closed').
        :param limit: Maximum number of orders to fetch.
        :param offset: Offset for pagination.
        :return: List of orders for the specified status.
        """
        return self.dao.fetch_orders_by_status(status, limit, offset)

    def fetch_orders_by_symbol_and_status(
        self, symbol: str, status: OrderStatus, limit: int = 100, offset: int = 0
    ) -> list:
        """Fetch orders by symbol and status with pagination.
        :param symbol: The stock symbol of the orders to fetch.
        :param status: The status of the orders to fetch (e.g., 'open', 'closed').
        :param limit: Maximum number of orders to fetch.
        :param offset: Offset for pagination.
        :return: List of orders matching the specified symbol and status.
        """
        return self.dao.fetch_orders_by_symbol_and_status(symbol, status, limit, offset)

    def insert_order(
        self,
        symbol: str,
        market: str,
        order_type: OrderType,
        status: OrderStatus,
        action: OrderAction,
        quantity: int,
        price: float,
        signal_id: str,
    ) -> int:
        """Insert a new order record.
        :param symbol: The stock symbol of the order.
        :param market: The market where the order is placed (e.g., 'NYSE', 'NASDAQ').
        :param order_type: The type of the order (e.g., 'market', 'limit').
        :param status: The status of the order (e.g., 'open', 'closed').
        :param action: The action of the order (e.g., 'buy', 'sell').
        :param quantity: The quantity of the order.
        :param price: The price at which the order was placed.
        :param signal_id: The ID of the signal associated with the order.
        :param user_id: The ID of the user who placed the order.
        :param account_id: The ID of the account associated with the order.
        :return: The ID of the newly inserted order.
        """
        return self.dao.insert_order(
            symbol,
            market,
            order_type,
            status,
            action,
            quantity,
            price,
            signal_id,
            self.user_id,
            self.account_id,
        )

    def update_order_status(self, order_id: int, new_status: OrderStatus) -> int:
        """Update the status of an existing order.
        :param order_id: The ID of the order to update.
        :param new_status: The new status to set for the order (e.g., 'open', 'closed').
        :return: The number of rows affected by the update.
        """
        return self.dao.update_order_status(order_id, new_status)

    def fill_order(
        self,
        order_id: int,
        fill_quantity: int,
        fill_price: float,
        executed_at: datetime,
        notes: str = "",
    ) -> bool:
        """Fill an existing order.
        :param order_id: The ID of the order to fill.
        :param filled_quantity: The quantity of the order that was filled.
        :param filled_price: The price at which the order was filled.
        :param user_id: The ID of the user who placed the order.
        :param account_id: The ID of the account associated with the order.
        :return: The number of rows affected by the fill operation.
        """
        order = self.dao.get_order_by_id(
            order_id=order_id, user_id=self.user_id, account_id=self.account_id
        )
        if not order:
            self.logger.warning(
                f"Order with ID {order_id} not found for user {self.user_id} and account {self.account_id}."
            )
            return False
        if not order_id:
            self.logger.warning(
                f"Order with ID {order_id} not found for user {self.user_id} and account {self.account_id}."
            )
            return False
        order_status = order.get("status")
        if fill_quantity <= 0 or fill_price <= 0:
            self.logger.warning(
                f"Invalid fill parameters: quantity={fill_quantity}, price={fill_price}."
            )
            return False
        if not order:
            self.logger.warning(
                f"Order with ID {order_id} not found for user {self.user_id} and account {self.account_id}."
            )
            return False
        if order_status != "open":
            self.logger.warning(
                f"Order with ID {order_id} is not open. Current status: {order_status}."
            )
            return False
        if fill_quantity <= 0 or fill_price <= 0:
            self.logger.warning(
                f"Invalid fill parameters: quantity={fill_quantity}, price={fill_price}."
            )
            return False
        current_position = self.position_dao.fetch_position_by_symbol(
            symbol=order["symbol"],
            user_id=self.user_id,
            account_id=self.account_id,
        )
        current_shares = current_position[0]["quantity"] if current_position else 0

        # Create Trade
        inserted_trade_id = self._insert_trade(
            order=order,
            fill_quantity=fill_quantity,
            fill_price=fill_price,
            executed_at=executed_at,
            notes=notes,
        )

        # Calculate remaining shares to fill
        remaining_shares_to_fill = order["quantity"] - current_shares
        # Update fill quantity and order status if necessary
        if fill_quantity >= remaining_shares_to_fill:
            self.logger.warning(
                f"Filled quantity {fill_quantity} exceeds remaining shares {remaining_shares_to_fill}. Correcting to remaining shares."
            )
            fill_quantity = remaining_shares_to_fill
            order_status = OrderStatus.FILLED
        else:
            self.logger.debug(
                f"Filling order {order_id} with quantity {fill_quantity} at price {fill_price}."
            )
            order_status = OrderStatus.PARTIALLY_FILLED

        # Upsert Position
        upserted_position_id = self._insert_position(
            order=order,
            fill_quantity=fill_quantity,
            fill_price=fill_price,
            inserted_trade_id=inserted_trade_id,
            current_shares=current_shares,
        )
        if upserted_position_id == -1:
            self.logger.error(
                f"Failed to upsert position for symbol {order['symbol']} with quantity {current_shares} at price {fill_price}."
            )
            return False

        # Update Order
        updated_order_id = self.dao.update_order_status(order_id, order_status)
        if updated_order_id == -1:
            self.logger.error(f"Failed to update order status for order {order_id}.")
            return False
        return True

    def _insert_trade(
        self,
        order: dict,
        fill_quantity: int,
        fill_price: float,
        executed_at: datetime,
        notes: str,
    ) -> int:
        # Create Trade
        order_id = order["id"]
        if not order_id:
            self.logger.error(
                f"Failed to insert trade for order {order_id} due to missing order ID."
            )
            return -1
        order_symbol = order["symbol"]
        if not order_symbol:
            self.logger.error(
                f"Failed to insert trade for order {order_id} due to missing symbol."
            )
            return -1
        order_action = order["action"]
        if order_action not in [OrderAction.BUY, OrderAction.SELL]:
            self.logger.error(
                f"Invalid order action {order_action} for order {order_id}. Must be 'buy' or 'sell'."
            )
            return -1
        order_market = order["market"]
        if not order_market:
            self.logger.error(
                f"Failed to insert trade for order {order_id} due to missing market information."
            )
            return -1
        inserted_trade_id = self.trade_dao.insert_trade(
            symbol=order_symbol,
            market=order_market,
            action=order_action,
            price=fill_price,
            shares=fill_quantity,
            executed_at=executed_at,
            notes=notes,
            order_id=order_id,
            user_id=self.user_id,
            account_id=self.account_id,
        )
        if not inserted_trade_id or inserted_trade_id == -1:
            self.logger.error(
                f"Failed to insert trade for order {order_id} with quantity {fill_quantity} at price {fill_price}."
            )
            return False

        # Create Order Trade
        inserted_order_trade_id = self.order_trades_dao.insert_order_trade(
            order_id=order_id,
            trade_id=inserted_trade_id,
        )
        if not inserted_order_trade_id or inserted_order_trade_id == -1:
            self.logger.error(
                f"Failed to insert order trade for order {order_id} and trade {inserted_trade_id}."
            )
            return False
        return inserted_trade_id

    def _insert_position(
        self,
        order: dict,
        fill_quantity: int,
        fill_price: float,
        inserted_trade_id: int,
        current_shares: int,
    ) -> int:
        order_action = order["action"]
        if order_action not in [OrderAction.BUY, OrderAction.SELL]:
            self.logger.error(
                f"Failed to insert position for order {order['id']} due to invalid action {order_action}. Must be 'buy' or 'sell'."
            )
            return -1
        if order_action == OrderAction.BUY:
            # If it's a buy order, we need to add to the position
            current_shares += fill_quantity
        else:
            # If it's a sell order, we need to subtract from the position
            current_shares -= fill_quantity

        order_symbol = order["symbol"]
        if not order_symbol:
            self.logger.error(
                f"Failed to insert position for order {order['id']} due to missing symbol."
            )
            return -1
        upserted_position_id = self.position_dao.upsert_position(
            symbol=order_symbol,
            quantity=current_shares,
            price=fill_price,
            user_id=self.user_id,
            account_id=self.account_id,
        )
        if not upserted_position_id or upserted_position_id == -1:
            self.logger.error(
                f"Failed to upsert position for symbol {order['symbol']} with quantity {current_shares} at price {fill_price}."
            )
            return -1
        # Update Position Trades
        self.position_trades_dao.insert_position_trade(
            position_id=upserted_position_id,
            trade_id=inserted_trade_id,
        )
        if not upserted_position_id or upserted_position_id == -1:
            self.logger.error(
                f"Failed to upsert position for symbol {order_symbol} with quantity {current_shares} at price {fill_price}."
            )
            return -1
        return upserted_position_id

    def delete_order(self, order_id: int) -> int:
        """Delete an order by its ID.
        :param order_id: The ID of the order to delete.
        :return: The number of rows affected by the deletion.
        """
        return self.dao.delete_order(order_id)

    def delete_all_orders(self) -> int:
        """Delete all orders from the database.
        :return: The number of rows affected by the deletion.
        """
        return self.dao.delete_all_orders()

    def _fetch_all_trades_by_order_id(self, order_id: int) -> list:
        """Fetch all trades by order ID with pagination.
        :param order_id: The ID of the order to fetch.
        :param limit: Maximum number of trades to fetch per batch.
        :param offset: Offset for pagination.
        :return: List of trades matching the specified order ID.
        """
        limit = 100
        offset = 0
        all_trades = []
        while True:
            trades = self.order_trades_dao.fetch_order_trades_by_order_id(
                order_id, limit, offset
            )
            if not trades:
                break
            all_trades.extend(trades)
            if len(trades) < limit:
                break
            offset += limit
        return all_trades
