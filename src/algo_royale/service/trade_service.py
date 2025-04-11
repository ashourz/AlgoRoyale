## service\trade_service.py
from datetime import datetime
from decimal import Decimal
from src.algo_royale.db.dao.trades_dao import TradesDAO

class TradeService:
    def __init__(self):
        self.trades_dao = TradesDAO()

    def create_trade(self, symbol: str, direction: str, entry_price: Decimal, shares: int, strategy_phase: str, entry_time: datetime, notes: str = '') -> None:
        """Create a new trade record."""
        self.trades_dao.insert_trade(symbol, direction, entry_price, shares, strategy_phase, entry_time, notes)

    def update_trade(self, trade_id: int, exit_price: Decimal, exit_time: datetime, pnl: Decimal) -> None:
        """Update an existing trade record."""
        self.trades_dao.update_trade(trade_id, exit_price, exit_time, pnl)

    def get_trade_by_id(self, trade_id: int):
        """Get trade details by trade ID."""
        return self.trades_dao.fetch_trade_by_id(trade_id)

    def calculate_trade_pnl(self, entry_price: Decimal, exit_price: Decimal, shares: int) -> Decimal:
        """Calculate the profit or loss of a trade."""
        return (exit_price - entry_price) * shares
