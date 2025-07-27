from datetime import datetime
from decimal import Decimal

from pyparsing import ABC

from algo_royale.services.db.trade_service import TradeService


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
    """A repository for managing trades."""

    def __init__(self, trade_service: TradeService):
        self.trade_service = trade_service
        self.fetch_page_size = 10

    def get_trades(self, limit: int = None, offset: int = 0) -> list:
        return self.trade_service.get_trades(
            limit=self.fetch_page_size if limit is None else limit, offset=offset
        )

    def add_trade(self, trade):
        self.trade_service.create_trade(trade)

    def update_trade(self, trade_id, updated_trade):
        self.trade_service.update_trade(trade_id, updated_trade)

    def _get_trade_pnl(self, trade_entry: TradeEntry) -> Decimal:
        """Calculate the profit or loss of a trade."""
