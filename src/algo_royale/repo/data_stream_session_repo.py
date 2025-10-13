import datetime
from uuid import UUID

from algo_royale.clients.db.dao.data_stream_session_dao import DataStreamSessionDAO
from algo_royale.logging.loggable import Loggable
from algo_royale.models.db.db_data_stream_session import DBDataStreamSession


class DataStreamSessionRepo:
    def __init__(
        self, dao: DataStreamSessionDAO, logger: Loggable, application_env: str
    ):
        self.dao = dao
        self.logger = logger
        self.application_env = application_env

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
        stream_class_name: str,
        symbol: str,
        start_time: datetime,
    ) -> UUID | None:
        """
        Insert a new data stream session.
        :param stream_class_name: The class name performing the data streaming.
        :param symbol: The symbol associated with the data stream (e.g., 'AAPL').
        :param application_env: The application environment (e.g., 'production', 'staging').
        :param start_time: The start time of the data stream session.
        :return: The ID of the newly created session, or -1 if the insertion failed.
        """
        return self.dao.insert_data_stream_session(
            stream_class=stream_class_name,
            symbol=symbol,
            application_env=self.application_env,
            start_time=start_time,
        )

    def update_data_stream_session_end_time(
        self, session_id: UUID, end_time: datetime
    ) -> UUID | None:
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
