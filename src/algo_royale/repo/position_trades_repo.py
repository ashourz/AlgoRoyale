from logging import Logger

from algo_royale.clients.db.dao.position_trades_dao import PositionTradesDAO


class PositionTradesRepo:
    def __init__(self, dao: PositionTradesDAO, logger: Logger):
        self.dao = dao
        self.logger = logger

    def insert_position_trade(self, position_id: int, trade_id: int) -> int:
        try:
            return self.dao.insert_position_trade(position_id, trade_id)
        except Exception as e:
            self.logger.error(f"Error inserting position trade: {e}")
            return -1

    def fetch_position_trades_by_position_id(self, position_id: int) -> list:
        try:
            return self.dao.fetch_position_trades_by_position_id(position_id)
        except Exception as e:
            self.logger.error(
                f"Error fetching position trades for position {position_id}: {e}"
            )
            return []

    def fetch_position_trades_by_trade_id(self, trade_id: int) -> list:
        try:
            return self.dao.fetch_position_trades_by_trade_id(trade_id)
        except Exception as e:
            self.logger.error(
                f"Error fetching position trades for trade {trade_id}: {e}"
            )
            return []

    def delete_all_position_trades(self) -> int:
        try:
            return self.dao.delete_all_position_trades()
        except Exception as e:
            self.logger.error(f"Error deleting all position trades: {e}")
            return -1
