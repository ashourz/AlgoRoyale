## service\trade_service.py
from abc import ABC
from datetime import datetime
from decimal import Decimal

from algo_royale.clients.db.dao.trade_dao import TradeDAO
from algo_royale.logging.loggable import Loggable


class TradeDirection(ABC):
    BUY = "BUY"
    SELL = "SELL"

    @classmethod
    def choices(cls):
        return [(cls.BUY, "Buy"), (cls.SELL, "Sell")]


class TradeEntry:
    def __init__(
        self,
        trade_id: str,
        symbol: str,
        direction: TradeDirection,
        execution_price: Decimal,
        shares: int,
        timestamp: datetime,
        notes: str = "",
    ):
        self.trade_id = trade_id
        self.symbol = symbol
        self.direction = direction
        self.execution_price = execution_price
        self.shares = shares
        self.timestamp = timestamp
        self.notes = notes


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

    def fetch_unsettled_trades(self, limit: int = 100, offset: int = 0) -> list:
        """Fetch all unsettled trades with pagination.
        :param limit: Maximum number of trades to fetch.
        :param offset: Offset for pagination.
        :return: List of unsettled trades.
        """
        return self.dao.fetch_unsettled_trades(limit, offset)

    def insert_trade(
        self,
        symbol: str,
        market: str,
        action: str,
        settlement_date: datetime,
        entry_price: Decimal,
        exit_price: Decimal,
        shares: int,
        entry_time: datetime,
        exit_time: datetime,
        notes: str,
        order_id: int,
    ) -> int:
        """Insert a new trade record.
        :param symbol: The stock symbol of the trade.
        :param market: The market where the trade occurred (e.g., 'NYSE', 'NASDAQ').
        :param action: The action of the trade (e.g., 'buy', 'sell').
        :param settlement_date: The settlement date of the trade.
        :param entry_price: The entry price of the trade.
        :param exit_price: The exit price of the trade.
        :param shares: The number of shares traded.
        :param entry_time: The time when the trade was entered.
        :param exit_time: The time when the trade was exited.
        :param notes: Additional notes about the trade.
        :param order_id: The ID of the associated order.
        :return: The ID of the newly inserted trade record.
        """
        return self.dao.insert_trade(
            symbol,
            market,
            action,
            settlement_date,
            entry_price,
            exit_price,
            shares,
            entry_time,
            exit_time,
            notes,
            order_id,
            self.user_id,
            self.account_id,
        )

    def fetch_trades_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
        offset: int = 0,
    ) -> list:
        """Fetch trades within a specific date range.
        :param start_date: The start date of the range.
        :param end_date: The end date of the range.
        :param limit: The maximum number of trades to return.
        :param offset: The number of trades to skip.
        :return: A list of trades within the specified date range.
        """
        return self.dao.fetch_trades_by_date_range(start_date, end_date, limit, offset)

    def update_trade_as_settled(self, trade_id: int) -> int:
        """Update a trade as settled."""
        return self.dao.update_trade_as_settled(trade_id)

    def delete_trade(self, trade_id: int) -> int:
        """Delete a trade record.
        :param trade_id: The ID of the trade to delete.
        :return: Number of deleted records."""
        return self.dao.delete_trade(trade_id)

    def delete_all_trades(self) -> int:
        """Delete all trade records.
        This is a destructive operation and should be used with caution.
        :return: Number of deleted records.
        """
        return self.dao.delete_all_trades()
