import datetime

from algo_royale.clients.db.dao.data_stream_session_dao import DataStreamSessionDAO
from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_data_stream_session import DBDataStreamSession


class DataStreamSessionRepo:
    def __init__(self, dao: DataStreamSessionDAO, logger: Loggable):
        self.dao = dao
        self.logger = logger

    def fetch_data_stream_session_by_timestamp(
        self, start_timestamp: datetime, end_timestamp: datetime
    ) -> list[DBDataStreamSession]:
        """
        Fetch data stream sessions within a specific timestamp range.
        :param start_timestamp: The start timestamp to filter sessions.
        :param end_timestamp: The end timestamp to filter sessions.
        :return: A list of DBDataStreamSession objects.
        """
        return self.dao.fetch_data_stream_session_by_timestamp(
            start_timestamp, end_timestamp
        )

    def insert_data_stream_session(
        self,
        stream_type: str,
        symbol: str,
        strategy_name: str,
        start_time: datetime,
    ) -> int:
        """
        Insert a new data stream session.
        :param stream_type: The type of the data stream (e.g., 'live', 'historical').
        :param symbol: The symbol associated with the data stream (e.g., 'AAPL').
        :param strategy_name: The name of the trading strategy being used.
        :param start_time: The start time of the data stream session.
        :return: The ID of the newly created session, or -1 if the insertion failed.
        """
        return self.dao.insert_data_stream_session(
            stream_type, symbol, strategy_name, start_time
        )

    def update_data_stream_session_end_time(
        self, session_id: int, end_time: datetime
    ) -> int:
        """
        Update the end time of an existing data stream session.
        :param session_id: The ID of the session to update.
        :param end_time: The new end time for the session.
        :return: The number of rows affected by the update.
        """
        return self.dao.update_data_stream_session_end_time(session_id, end_time)

    def delete_all_data_stream_sessions(self) -> int:
        """
        Delete all data stream sessions from the database.
        :return: The number of rows deleted.
        """
        return self.dao.delete_all_data_stream_session()
