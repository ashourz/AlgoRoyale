# src/algo_royale/db/dao/trade_signals_dao.py
from src.algo_royale.db.dao.base_dao import BaseDAO
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Tuple

class TradeSignalsDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_all_signals(self) -> List[Tuple[int, str, str, Decimal, datetime]]:
        """Fetch all trade signals."""
        return self.fetch("get_all_signals.sql", [])

    def fetch_signal_by_id(self, signal_id: int) -> Optional[Tuple[int, str, str, Decimal, datetime]]:
        """Fetch a trade signal by its ID."""
        return self.fetch("get_signal_by_id.sql", (signal_id,))

    def insert_signal(self, symbol: str, signal: str, price: decimal, created_at: datetime) -> None:
        """Insert a new trade signal."""
        return self.insert("insert_signal.sql", (symbol, signal, price, created_at))

    def update_signal(self, signal_id: int, symbol: str, signal: str, price: decimal, created_at: datetime) -> None:
        """Update an existing trade signal."""
        return self.update("update_signal.sql", (symbol, signal, price, created_at, signal_id))

    def delete_signal(self, signal_id: int) -> None:
        """Delete a trade signal by its ID."""
        return self.delete("delete_signal.sql", (signal_id,))
