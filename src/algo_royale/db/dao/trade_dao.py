# db/dao/trade_dao.py
from db.dao.base_dao import BaseDAO

class TradeDAO(BaseDAO):
    def __init__(self):
        pass  # No need to keep a connection open permanently
    
    def get_recent_trades(self, symbol, limit=100):
        query = self._read_sql_file('get_recent_trades.sql')
        return self._execute(query, (symbol, limit), fetch=True)

    def insert_trade(self, symbol, price, trade_time):
        query = self._read_sql_file('insert_trade.sql')
        self._execute(query, (symbol, price, trade_time))
