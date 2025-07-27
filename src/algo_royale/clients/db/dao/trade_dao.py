# src/algo_royale/clients/db/dao/trade_dao.py
from datetime import datetime
from decimal import Decimal

import psycopg2

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.logging.loggable import Loggable


class TradeDAO(BaseDAO):
    def __init__(
        self,
        connection: psycopg2.extensions.connection,
        sql_dir: str,
        logger: Loggable,
    ):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_unsettled_trades(self, limit: int = 100, offset: int = 0) -> list:
        """Fetch all unsettled trades with pagination."""
        return self.fetch("get_unsettled_trades.sql", (limit, offset))

    def insert_trade(
        self,
        symbol: str,
        market: str,
        order_type: str,
        action: str,
        settlment_date: datetime,
        entry_price: Decimal,
        exit_price: Decimal,
        shares: int,
        entry_time: datetime,
        exit_time: datetime,
        realized_pnl: Decimal,
        notes: str,
        order_id: int,
        user_id: int,
        account_id: int,
    ) -> int:
        """Insert a new trade record.
        :param symbol: The stock symbol of the trade.
        :param market: The market where the trade occurred (e.g., 'NYSE', 'NASDAQ').
        :param order_type: The type of the order (e.g., 'market', 'limit').
        :param action: The action of the trade (e.g., 'buy', 'sell').
        :param settlement_date: The settlement date of the trade.
        :param entry_price: The entry price of the trade.
        :param exit_price: The exit price of the trade.
        :param shares: The number of shares traded.
        :param entry_time: The time when the trade was entered.
        :param exit_time: The time when the trade was exited.
        :param realized_pnl: The realized profit and loss from the trade.
        :param notes: Additional notes about the trade.
        :param order_id: The ID of the associated order.
        :param user_id: The ID of the user who made the trade.
        :param account_id: The ID of the account associated with the trade.
        :return: The ID of the newly inserted trade.
        """
        return self.insert(
            "insert_trade.sql",
            (
                symbol,
                market,
                order_type,
                action,
                settlment_date,
                entry_price,
                exit_price,
                shares,
                entry_time,
                exit_time,
                realized_pnl,
                notes,
                order_id,
                user_id,
                account_id,
            ),
        )

    def update_trade_as_settled(self, trade_id: int) -> int:
        """Update a trade record as settled by its ID.
        :param trade_id: The ID of the trade to update.
        :return: The ID of the updated trade.
        """
        return self.update("update_trade.sql", (trade_id,))

    def delete_trade(self, trade_id: int) -> int:
        """Delete a trade record by its ID.
        :param trade_id: The ID of the trade to delete.
        :return: The ID of the deleted trade.
        """
        return self.delete("delete_trade.sql", (trade_id,))

    def delete_all_trades(self) -> int:
        """Delete all trade records.
        :return: The number of deleted trades.
        """
        deleted_ids = self.delete("delete_all_trades.sql", ())
        return len(deleted_ids) if deleted_ids else 0
