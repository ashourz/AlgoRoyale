# db/dao/signal_dao.py
from src.algo_royale.db.dao.base_dao import BaseDAO
from src.algo_royale.db.db import connect_db

class SignalDAO(BaseDAO):
    def __init__(self):
        super().__init__(connect_db())

    def get_signals_by_symbol(self, symbol: str):
        return self.fetch('get_signals_by_symbol.sql', (symbol,), log_name="get_signals_by_symbol")

    def insert_signal(self, symbol: str, signal: str, price: float, created_at):
        self.insert('insert_signal.sql', (symbol, signal, price, created_at), log_name="insert_signal")

    def update_signal_confidence(self, signal_id: int, new_confidence: float):
        self.update('update_signal_confidence.sql', (new_confidence, signal_id), log_name="update_confidence")

    def delete_old_signals(self, cutoff_date):
        self.delete('delete_old_signals.sql', (cutoff_date,), log_name="delete_old_signals")