## service\trade_service.py
from datetime import datetime
from decimal import Decimal
from algo_royale.clients.db.dao.trade_dao import TradeDAO
from typing import List, Tuple

class TradeService:
    def __init__(self, dao: TradeDAO):
        self.dao = dao

    def create_trade(self, symbol: str, direction: str, entry_price: Decimal, shares: int, strategy_phase: str, entry_time: datetime, notes: str = '') -> None:
        """Create a new trade record."""
        self.trade_dao.insert_trade(symbol, direction, entry_price, shares, strategy_phase, entry_time, notes)

    def update_trade(self, trade_id: int, exit_price: Decimal, exit_time: datetime, pnl: Decimal) -> None:
        """Update an existing trade record."""
        self.trade_dao.update_trade(trade_id, exit_price, exit_time, pnl)

    def get_trade_by_id(self, trade_id: int) -> Tuple:
        """Get trade details by trade ID."""
        return self.trade_dao.fetch_trade_by_id(trade_id)

    def get_trades_by_symbol(self, symbol: str, limit: int = 10, offset: int = 0) -> List[Tuple]:
        """Get trades by stock symbol."""
        return self.trade_dao.fetch_trades_by_symbol(symbol, limit, offset)

    def calculate_trade_pnl(self, entry_price: Decimal, exit_price: Decimal, shares: int) -> Decimal:
        """Calculate the profit or loss of a trade."""
        return (exit_price - entry_price) * shares

    def get_trade_history(self, limit: int = 10, offset: int = 0) -> List[Tuple]:
        """Get trade history with pagination."""
        return self.trade_dao.fetch_trades(limit, offset)
    
    def get_trades_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Tuple]:
        """Get trades within a specific date range."""
        return self.trade_dao.fetch_trades_by_date_range(start_date, end_date)
    
    def get_open_trades(self) -> List[Tuple]:
        """Get all open trades."""
        return self.trade_dao.fetch_open_trades()
    
    def get_trades_by_symbol_and_date(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Tuple]:
        """Get trades by symbol and date range."""
        return self.trade_dao.fetch_trades_by_symbol_and_date(symbol, start_date, end_date)
    

    def delete_trade(self, trade_id: int) -> None:
        self.trade_dao.delete_trade(trade_id)