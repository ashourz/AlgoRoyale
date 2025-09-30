# src/algo_royale/clients/db/dao/trade_dao.py
from datetime import datetime
from decimal import Decimal
from uuid import UUID

import psycopg2

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_position import DBPosition
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
        rows = self.fetch("fetch_unsettled_trades.sql", (limit, offset))
        return [DBTrade.from_tuple(row) for row in rows]

    def fetch_open_positions(self, user_id: str, account_id: str) -> list[DBPosition]:
        """Fetch all open positions.
        :return: List of open positions.
        """
        rows = self.fetch("fetch_open_positions.sql", (user_id, account_id))
        return [DBPosition.from_tuple(row) for row in rows]

    def fetch_trades_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: str = 100,
        offset: str = 0,
    ) -> list[DBTrade]:
        """Fetch trades within a specific date range."""
        rows = self.fetch(
            "fetch_trades_by_date_range.sql",
            (start_date, end_date, limit, offset),
        )
        return [DBTrade.from_tuple(row) for row in rows]

    def fetch_trades_by_order_id(self, order_id: UUID) -> list[DBTrade]:
        """Fetch trades by order ID."""
        rows = self.fetch("get_trades_by_order_id.sql", (str(order_id),))
        return [DBTrade.from_tuple(row) for row in rows]

    def insert_trade(
        self,
        symbol: str,
        action: str,
        settlement_date: datetime,
        price: Decimal,
        quantity: int,
        executed_at: datetime,
        order_id: UUID,
        user_id: str,
        account_id: str,
    ) -> UUID | None:
        """Insert a new trade record.
        :param symbol: The stock symbol of the trade.
        :param market: The market where the trade occurred (e.g., 'NYSE', 'NASDAQ').
        :param action: The action of the trade (e.g., 'buy', 'sell').
        :param settlement_date: The date when the trade is settled.
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
                action,
                settlement_date,
                price,
                quantity,
                executed_at,
                str(order_id),
                user_id,
                account_id,
            ),
        )
        if not returned_id:
            self.logger.error(
                f"Failed to insert trade for symbol {symbol} with action {action}."
            )
            return None
        return returned_id

    def update_settled_trades(self, settlement_datetime: datetime) -> int:
        """Update all settled trades in the database.
        :return: The number of updated trade records, or -1 if the update failed.
        """
        update_count = self.update("update_settled_trades.sql", (settlement_datetime,))
        if update_count < 0:
            self.logger.error(
                "Failed to update settled trades | update count: {update_count}"
            )
            return -1
        return update_count

    def delete_trade(self, trade_id: UUID) -> int:
        """Delete a trade record by its ID.
        :param trade_id: The ID of the trade to delete.
        :return: The ID of the deleted trade, or -1 if the deletion failed.
        """
        delete_count = self.delete("delete_trade.sql", (trade_id,))
        if not delete_count:
            self.logger.error(f"Failed to delete trade {trade_id}.")
            return -1
        return delete_count

    def delete_all_trades(self) -> int:
        """Delete all trade records.
        :return: The number of deleted trades, or -1 if the deletion failed.
        """
        delete_count = self.delete("delete_all_trades.sql", ())
        return delete_count or -1
