from datetime import datetime

from algo_royale.clients.db.dao.data_stream_session_dao import DataStreamSessionDAO
from algo_royale.models.db.db_data_stream_session import DBDataStreamSession


class MockDataStreamSessionDAO(DataStreamSessionDAO):
    def __init__(self):
        from uuid import UUID

        now = datetime.now()
        self.base_session = DBDataStreamSession(
            id=UUID("123e4567-e89b-12d3-a456-426614174abc"),
            stream_type="live",
            symbol="AAPL",
            strategy_name="test_strategy",
            start_time=now,
            end_time=now,
        )
        self.test_session = self.base_session

    def reset_session(self):
        self.test_session = self.base_session

    def reset(self):
        self.reset_session()

    def fetch_data_stream_session_by_timestamp(
        self, start_timestamp: datetime, end_timestamp: datetime
    ) -> list[DBDataStreamSession]:
        return [self.test_session]

    def insert_data_stream_session(
        self, stream_type: str, symbol: str, strategy_name: str, start_time: datetime
    ) -> int:
        return 1

    def update_data_stream_session_end_time(
        self, session_id: int, end_time: datetime
    ) -> int:
        return 1

    def delete_all_data_stream_session(self) -> int:
        return 1
