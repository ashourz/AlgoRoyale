# src/algo_royale/db/dao/trades_dao.py
import decimal
import datetime
from src.algo_royale.db.dao.base_dao import BaseDAO

class TradesDAO(BaseDAO):
    def __init__(self):
        super().__init__()

    def fetch_all_trades(self):
        return self.fetch("get_all_trades.sql", [])

    def fetch_trade_by_id(self, trade_id: int):
        return self.fetch("get_trade_by_id.sql", (trade_id,))

    def insert_trade(self, symbol: str, direction: str, entry_price: decimal, exit_price: decimal, shares: int,
                     entry_time: datetime, exit_time: datetime, strategy_phase: str, pnl: decimal, notes: str):
        return self.insert(
            "insert_trade.sql",
            (symbol, direction, entry_price, exit_price, shares, entry_time, exit_time, strategy_phase, pnl, notes)
        )

    def update_trade(self, trade_id: int, symbol: str, direction: str, entry_price: decimal, exit_price: decimal,
                     shares: int, entry_time: datetime, exit_time: datetime, strategy_phase: str, pnl: decimal,
                     notes: str):
        return self.update(
            "update_trade.sql",
            (symbol, direction, entry_price, exit_price, shares, entry_time, exit_time, strategy_phase, pnl, notes, trade_id)
        )

    def delete_trade(self, trade_id: int):
        return self.delete("delete_trade.sql", (trade_id,))
