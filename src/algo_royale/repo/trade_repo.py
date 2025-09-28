## service\trade_service.py
from abc import ABC
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from algo_royale.clients.db.dao.trade_dao import TradeDAO
from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_position import DBPosition
from algo_royale.models.db.db_trade import DBTrade


class TradeDirection(ABC):
    BUY = "BUY"
    SELL = "SELL"

    @classmethod
    def choices(cls):
        return [(cls.BUY, "Buy"), (cls.SELL, "Sell")]


class TradeRepo:
    def __init__(
        self,
        dao: TradeDAO,
        logger: Loggable,
        user_id: str,
        account_id: str,
    ):
        self.dao = dao
        self.logger = logger
        self.user_id = user_id
        self.account_id = account_id

    def fetch_unsettled_trades(
        self, limit: int = 100, offset: int = 0
    ) -> list[DBTrade]:
        """Fetch all unsettled trades with pagination.
        :param limit: Maximum number of trades to fetch.
        :param offset: Offset for pagination.
        :return: List of unsettled trades.
        """
        return self.dao.fetch_unsettled_trades(limit, offset)

    def insert_trade(
        self,
        symbol: str,
        action: str,
        settlement_date: datetime,
        price: Decimal,
        quantity: int,
        executed_at: datetime,
        order_id: UUID,
    ) -> UUID | None:
        """Insert a new trade record.
        :param symbol: The stock symbol of the trade.
        :param market: The market where the trade occurred (e.g., 'NYSE', 'NASDAQ').
        :param action: The action of the trade (e.g., 'buy', 'sell').
        :param settlement_date: The settlement date of the trade.
        :param entry_price: The entry price of the trade.
        :param exit_price: The exit price of the trade.
        :param quantity: The number of shares traded.
        :param executed_at: The time when the trade was entered.
        :param order_id: The ID of the associated order.
        :return: The ID of the newly inserted trade record.
        """
        return self.dao.insert_trade(
            symbol,
            action,
            settlement_date,
            price,
            quantity,
            executed_at,
            order_id=order_id,
            user_id=self.user_id,
            account_id=self.account_id,
        )

    def fetch_open_positions(self) -> list[DBPosition]:
        """Fetch all open positions.
        :return: List of open positions.
        """
        return self.dao.fetch_open_positions(
            user_id=self.user_id,
            account_id=self.account_id,
        )

    def fetch_trades_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> list[DBTrade]:
        """Fetch trades within a specific date range.
        :param start_date: The start date of the range.
        :param end_date: The end date of the range.
        :param limit: The maximum number of trades to return.
        :param offset: The number of trades to skip.
        :return: A list of trades within the specified date range.
        """
        return self.dao.fetch_trades_by_date_range(start_date, end_date, limit, offset)

    def fetch_trades_by_order_id(self, order_id: UUID) -> list[DBTrade]:
        """Fetch trades by order ID."""
        return self.dao.fetch_trades_by_order_id(order_id)

    def update_settled_trades(self, settlement_datetime: datetime) -> int:
        """Update all trades as settled."""
        return self.dao.update_settled_trades(settlement_datetime)

    def delete_trade(self, trade_id: UUID) -> int:
        """Delete a trade record.
        :param trade_id: The ID of the trade to delete.
        :return: Number of deleted records."""
        return self.dao.delete_trade(str(trade_id))

    def delete_all_trades(self) -> int:
        """Delete all trade records.
        This is a destructive operation and should be used with caution.
        :return: Number of deleted records.
        """
        return self.dao.delete_all_trades()
