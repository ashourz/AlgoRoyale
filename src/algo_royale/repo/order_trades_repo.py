from logging import Logger

from algo_royale.clients.db.dao.order_trades_dao import OrderTradesDAO


class OrderTradesRepo:
    def __init__(self, dao: OrderTradesDAO, logger: Logger):
        self.dao = dao
        self.logger = logger

    def fetch_order_trades_by_order_id(self, order_id: int) -> list:
        try:
            return self.dao.fetch_order_trades_by_order_id(order_id)
        except Exception as e:
            self.logger.error(f"Error fetching order trades for order {order_id}: {e}")
            return []

    def fetch_trade_orders_by_trade_id(self, trade_id: int) -> list:
        try:
            return self.dao.fetch_trade_orders_by_trade_id(trade_id)
        except Exception as e:
            self.logger.error(f"Error fetching trade orders for trade {trade_id}: {e}")
            return []

    def insert_order_trade(self, order_id: int, trade_id: int) -> int:
        try:
            return self.dao.insert_order_trade(order_id, trade_id)
        except Exception as e:
            self.logger.error(f"Error inserting order trade: {e}")
            return -1

    def delete_all_order_trades(self) -> int:
        try:
            return self.dao.delete_all_order_trades()
        except Exception as e:
            self.logger.error(f"Error deleting all order trades: {e}")
            return -1
