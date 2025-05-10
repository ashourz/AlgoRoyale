## db\dao\trades_dao.py
from decimal import Decimal
from datetime import datetime
from typing import List, Tuple
from algo_royale.live_trading.db.dao.base_dao import BaseDAO

class TradesDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_trades(self, limit:int = 10, offset: int = 0) -> List[Tuple[int, str, str, Decimal, Decimal, int, datetime, datetime, str, Decimal, str]]:
        """Fetch all trades with pagination."""
        return self.fetch("get_all_trades.sql", (limit, offset))

    def fetch_trade_by_id(self, trade_id: int) -> Tuple[int, str, str, Decimal, Decimal, int, datetime, datetime, str, Decimal, str]:
        """Fetch a trade record by its ID."""
        return self.fetch("get_trade_by_id.sql", (trade_id,))
    
    def fetch_trades_by_symbol(self, symbol: str, limit:int = 10, offset: int = 0) -> List[Tuple[int, str, str, Decimal, Decimal, int, datetime, datetime, str, Decimal, str]]:
        """Fetch trades by stock symbol."""
        return self.fetch("get_trades_by_symbol.sql", (symbol, limit, offset))

    def fetch_trades_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Tuple[int, str, str, Decimal, Decimal, int, datetime, datetime, str, Decimal, str]]:
        """Fetch trades within a specific date range."""
        return self.fetch("get_trades_by_date_range.sql", (start_date, end_date))
    
    def fetch_trades_by_symbol_and_date(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Tuple[int, str, str, Decimal, Decimal, int, datetime, datetime, str, Decimal, str]]:
        """Fetch trades by symbol and date range."""
        return self.fetch("get_trades_by_symbol_and_date.sql", (symbol, start_date, end_date))
    
    def fetch_open_trades(self) -> List[Tuple[int, str, str, Decimal, Decimal, int, datetime, datetime, str, Decimal, str]]:
        """Fetch all open trades."""
        return self.fetch("get_open_trades.sql", [])


    def insert_trade(self, symbol: str, direction: str, entry_price: Decimal, exit_price: Decimal, shares: int,
                     entry_time: datetime, exit_time: datetime, strategy_phase: str, pnl: Decimal, notes: str) -> None:
        """Insert a new trade record."""
        return self.insert(
            "insert_trade.sql",
            (symbol, direction, entry_price, exit_price, shares, entry_time, exit_time, strategy_phase, pnl, notes)
        )

    def update_trade(self, trade_id: int, symbol: str, direction: str, entry_price: Decimal, exit_price: Decimal,
                     shares: int, entry_time: datetime, exit_time: datetime, strategy_phase: str, pnl: Decimal,
                     notes: str) -> None:
        """Update an existing trade record."""
        return self.update(
            "update_trade.sql",
            (symbol, direction, entry_price, exit_price, shares, entry_time, exit_time, strategy_phase, pnl, notes, trade_id)
        )

    def delete_trade(self, trade_id: int) -> None:
        """Delete a trade record by its ID."""
        return self.delete("delete_trade.sql", (trade_id,))