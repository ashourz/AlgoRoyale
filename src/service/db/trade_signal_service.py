## service\trade_signal_service.py
from datetime import datetime
from decimal import Decimal
from src.algo_royale.db.dao.trade_signals_dao import TradeSignalsDAO

class TradeSignalService:
    def __init__(self):
        self.trade_signals_dao = TradeSignalsDAO()

    def create_signal(self, symbol: str, signal: str, price: Decimal, created_at: datetime) -> None:
        """Insert a new trade signal."""
        self.trade_signals_dao.insert_signal(symbol, signal, price, created_at)

    def get_signals_by_symbol(self, symbol: str):
        """Fetch trade signals by symbol."""
        return self.trade_signals_dao.fetch_signals_by_symbol(symbol)

    def get_signal_by_id(self, signal_id: int):
        """Get signal details by ID."""
        return self.trade_signals_dao.fetch_signal_by_id(signal_id)
    
    def get_all_signals(self):
        """Fetch all trade signals."""
        return self.trade_signals_dao.fetch_all_signals()
    
    def update_signal(self, signal_id: int, symbol: str, signal: str, price: Decimal, created_at: datetime) -> None:
        """Update an existing trade signal."""
        self.trade_signals_dao.update_signal(signal_id, symbol, signal, price, created_at)
        
    def delete_signal(self, signal_id: int) -> None:
        """Delete a trade signal by its ID."""
        self.trade_signals_dao.delete_signal(signal_id)
    
    def get_signal_by_symbol_and_date(self, symbol: str, start_date: datetime, end_date: datetime):
        """Fetch trade signals by symbol and date."""
        return self.trade_signals_dao.fetch_signals_by_symbol_and_date(symbol, start_date, end_date)