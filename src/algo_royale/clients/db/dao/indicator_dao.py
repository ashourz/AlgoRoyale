## db\dao\indicators_dao.py
from logging import Logger
from algo_royale.clients.db.dao.base_dao import BaseDAO
from decimal import Decimal
from datetime import datetime
from typing import List, Tuple

import psycopg2

class IndicatorDAO(BaseDAO):
    def __init__(self, 
                 connection: psycopg2.extensions.connection, 
                 sql_dir: str,
                 logger: Logger):
        super().__init__(
            connection=connection,
            sql_dir=sql_dir,
            logger = logger
            )

    def fetch_indicators_by_trade_id(self, trade_id: int) -> List[Tuple[int, int, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, datetime]]:
        """Fetch indicators by trade ID."""
        return self.fetch("get_indicators_by_trade_id.sql", (trade_id,))
    
    def fetch_indicators_by_trade_id_and_date(self, trade_id: int, start_date: datetime, end_date: datetime) -> List[Tuple[int, int, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, Decimal, datetime]]:
        """Fetch indicators by trade ID and date range."""
        return self.fetch("get_indicators_by_trade_id_and_date.sql", (trade_id, start_date, end_date))


    def insert_indicator(self, trade_id: int, rsi: Decimal, macd: Decimal, macd_signal: Decimal, volume: Decimal,
                          bollinger_upper: Decimal, bollinger_lower: Decimal, atr: Decimal, price: Decimal,
                          ema_short: Decimal, ema_long: Decimal, recorded_at: datetime) -> None:
        """Insert new indicators."""
        return self.insert(
            "insert_indicators.sql",
            (trade_id, rsi, macd, macd_signal, volume, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at)
        )

    def update_indicator(self, indicator_id: int, rsi: Decimal, macd: Decimal, macd_signal: Decimal, volume: Decimal,
                          bollinger_upper: Decimal, bollinger_lower: Decimal, atr: Decimal, price: Decimal,
                          ema_short: Decimal, ema_long: Decimal, recorded_at: datetime) -> None:
        """Update existing indicators."""
        return self.update(
            "update_indicators.sql",
            (rsi, macd, macd_signal, volume, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at, indicator_id)
        )

    def delete_indicator(self, indicator_id: int) -> None:
        """Delete indicators by ID."""
        return self.delete("delete_indicators.sql", (indicator_id,))