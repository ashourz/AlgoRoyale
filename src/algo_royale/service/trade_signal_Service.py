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
