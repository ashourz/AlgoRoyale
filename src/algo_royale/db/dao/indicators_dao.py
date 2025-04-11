## db\dao\indicators_dao.py
from src.algo_royale.db.dao.base_dao import BaseDAO
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Tuple

class IndicatorsDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_indicators_by_trade_id(self, trade_id: int) -> List[Tuple[int, int, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, datetime]]:
        """Fetch indicators by trade ID."""
        return self.fetch("get_indicators_by_trade_id.sql", (trade_id,))

    def insert_indicators(self, trade_id: int, rsi: Decimal, macd: Decimal, macd_signal: Decimal, volume: Decimal,
                          bollinger_upper: Decimal, bollinger_lower: Decimal, atr: Decimal, price: Decimal,
                          ema_short: Decimal, ema_long: Decimal, recorded_at: datetime) -> None:
        """Insert new indicators."""
        return self.insert(
            "insert_indicators.sql",
            (trade_id, rsi, macd, macd_signal, volume, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at)
        )

    def update_indicators(self, indicator_id: int, rsi: Decimal, macd: Decimal, macd_signal: Decimal, volume: Decimal,
                          bollinger_upper: Decimal, bollinger_lower: Decimal, atr: Decimal, price: Decimal,
                          ema_short: Decimal, ema_long: Decimal, recorded_at: datetime) -> None:
        """Update existing indicators."""
        return self.update(
            "update_indicators.sql",
            (rsi, macd, macd_signal, volume, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at, indicator_id)
        )

    def delete_indicators(self, indicator_id: int) -> None:
        """Delete indicators by ID."""
        return self.delete("delete_indicators.sql", (indicator_id,))