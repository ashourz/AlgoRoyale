# src/algo_royale/db/dao/indicators_dao.py
from src.algo_royale.db.dao.base_dao import BaseDAO

class IndicatorsDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_indicators_by_trade_id(self, trade_id: int):
        return self.fetch("get_indicators_by_trade_id.sql", (trade_id,))

    def insert_indicators(self, trade_id: int, rsi: decimal, macd: decimal, macd_signal: decimal, volume: decimal,
                          bollinger_upper: decimal, bollinger_lower: decimal, atr: decimal, price: decimal,
                          ema_short: decimal, ema_long: decimal, recorded_at: datetime):
        return self.insert(
            "insert_indicators.sql",
            (trade_id, rsi, macd, macd_signal, volume, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at)
        )

    def update_indicators(self, indicator_id: int, rsi: decimal, macd: decimal, macd_signal: decimal, volume: decimal,
                          bollinger_upper: decimal, bollinger_lower: decimal, atr: decimal, price: decimal,
                          ema_short: decimal, ema_long: decimal, recorded_at: datetime):
        return self.update(
            "update_indicators.sql",
            (rsi, macd, macd_signal, volume, bollinger_upper, bollinger_lower, atr, price, ema_short, ema_long, recorded_at, indicator_id)
        )

    def delete_indicators(self, indicator_id: int):
        return self.delete("delete_indicators.sql", (indicator_id,))
