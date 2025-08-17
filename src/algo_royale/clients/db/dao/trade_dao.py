# src/algo_royale/clients/db/dao/trade_dao.py
from datetime import datetime
from decimal import Decimal

import psycopg2

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_trade import DBTrade


class TradeDAO(BaseDAO):
    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        sql_dir: str,
        logger: Loggable,
    ):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_unsettled_trades(
        self, limit: int = 100, offset: int = 0
    ) -> list[DBTrade]:
        """Fetch all unsettled trades with pagination."""
        rows = self.fetch("get_unsettled_trades.sql", (limit, offset))
        return [DBTrade.from_tuple(row) for row in rows]

    def fetch_trades_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DBTrade]:
        """Fetch trades within a specific date range."""
        rows = self.fetch(
            "get_trades_by_date_range.sql",
            (start_date, end_date, limit, offset),
        )
        return [DBTrade.from_tuple(row) for row in rows]

    def insert_trade(
        self,
        symbol: str,
        market: str,
        action: str,
        price: Decimal,
        quantity: int,
        executed_at: datetime,
        order_id: int,
        user_id: int,
        account_id: int,
    ) -> int:
        """Insert a new trade record.
        :param symbol: The stock symbol of the trade.
        :param market: The market where the trade occurred (e.g., 'NYSE', 'NASDAQ').
        :param action: The action of the trade (e.g., 'buy', 'sell').
        :param price: The execution price of the trade.
        :param quantity: The number of shares traded.
        :param executed_at: The time when the trade was executed.
        :param notes: Additional notes about the trade.
        :param order_id: The ID of the associated order.
        :param user_id: The ID of the user who made the trade.
        :param account_id: The ID of the account associated with the trade.
        :return: The ID of the newly inserted trade record, or -1 if the insertion failed.
        """
        returned_id = self.insert(
            "insert_trade.sql",
            (
                symbol,
                market,
                action,
                price,
                quantity,
                executed_at,
                order_id,
                user_id,
                account_id,
            ),
        )
        if not returned_id:
            self.logger.error(
                f"Failed to insert trade for symbol {symbol} with action {action}."
            )
            return -1
        return returned_id

    def update_trade_as_settled(self, trade_id: int) -> int:
        """Update a trade record as settled by its ID.
        :param trade_id: The ID of the trade to update.
        :return: The ID of the updated trade record, or -1 if the update failed.
        """
        updated_id = self.update("update_trade.sql", (trade_id,))
        if not updated_id:
            self.logger.error(f"Failed to update trade {trade_id} as settled.")
            return -1
        return updated_id

    def delete_trade(self, trade_id: int) -> int:
        """Delete a trade record by its ID.
        :param trade_id: The ID of the trade to delete.
        :return: The ID of the deleted trade, or -1 if the deletion failed.
        """
        deleted_id = self.delete("delete_trade.sql", (trade_id,))
        if not deleted_id:
            self.logger.error(f"Failed to delete trade {trade_id}.")
            return -1
        return deleted_id

    def delete_all_trades(self) -> int:
        """Delete all trade records.
        :return: The number of deleted trades, or -1 if the deletion failed.
        """
        deleted_ids = self.delete("delete_all_trades.sql", ())
        return len(deleted_ids) if deleted_ids else -1
