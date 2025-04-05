# db/dao/trade_dao.py
from db.dao.base_dao import BaseDAO

class TradeDAO(BaseDAO):

    def get_recent_trades(self, symbol, limit=100):
        query = """
        SELECT * FROM trades
        WHERE symbol = %s
        ORDER BY trade_time DESC
        LIMIT %s
        """
        return self._execute(query, (symbol, limit), fetch=True)

    def insert_trade(self, symbol, price, trade_time):
        query = """
        INSERT INTO trades (symbol, price, trade_time)
        VALUES (%s, %s, %s)
        """
        self._execute(query, (symbol, price, trade_time))
