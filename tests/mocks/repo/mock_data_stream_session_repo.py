import datetime
from uuid import UUID

from algo_royale.models.db.db_data_stream_session import DBDataStreamSession
from algo_royale.repo.data_stream_session_repo import DataStreamSessionRepo
from tests.mocks.clients.db.mock_data_stream_session_dao import MockDataStreamSessionDAO
from tests.mocks.mock_loggable import MockLoggable


class MockDataStreamSessionRepo(DataStreamSessionRepo):
    def __init__(self):
        self.dao = MockDataStreamSessionDAO()
        self.logger = MockLoggable()
        super().__init__(dao=self.dao, logger=self.logger)
        self._return_empty = False
        self._raise_exception = False

    def reset_return_empty(self):
        self._return_empty = False

    def reset_raise_exception(self):
        self._raise_exception = False

    def reset_dao(self):
        self.dao.reset()

    def fetch_data_stream_session_by_timestamp(
        self, start_timestamp: datetime.datetime, end_timestamp: datetime.datetime
    ) -> list[DBDataStreamSession]:
        if self._raise_exception:
            raise ValueError("Database error")
        if self._return_empty:
            return []
        return self.dao.fetch_data_stream_session_by_timestamp(
            start_timestamp, end_timestamp
        )

    def insert_data_stream_session(
        self,
        stream_type: str,
        symbol: str,
        strategy_name: str,
        start_time: datetime.datetime,
    ) -> UUID | None:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.insert_data_stream_session(
            stream_type, symbol, strategy_name, start_time
        )

    def update_data_stream_session_end_time(
        self, session_id: UUID, end_time: datetime.datetime
    ) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.update_data_stream_session_end_time(session_id, end_time)

    def delete_all_data_stream_sessions(self) -> int:
        if self._raise_exception:
            raise ValueError("Database error")
        return self.dao.delete_all_data_stream_session()
