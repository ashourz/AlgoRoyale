from datetime import datetime
from uuid import UUID

from algo_royale.clients.db.dao.base_dao import BaseDAO
from algo_royale.models.db.db_data_stream_session import DBDataStreamSession


class DataStreamSessionDAO(BaseDAO):
    def __init__(self, connection, sql_dir, logger):
        super().__init__(connection=connection, sql_dir=sql_dir, logger=logger)

    def fetch_data_stream_session_by_timestamp(
        self, start_timestamp: datetime, end_timestamp: datetime
    ) -> list:
        """
        Fetch data stream session by timestamp.
        :param start_timestamp: The start timestamp to filter sessions.
        :param end_timestamp: The end timestamp to filter sessions.
        :return: A list of dictionaries containing the session data, or an empty list if not found.
        """
        rows = self.fetch(
            "fetch_data_stream_session_by_timestamp.sql",
            (start_timestamp, end_timestamp),
        )
        return [DBDataStreamSession.from_tuple(row) for row in rows] if rows else []

    def insert_data_stream_session(
        self,
        stream_class: str,
        symbol: str,
        application_env: str,
        start_time: datetime,
    ) -> UUID | None:
        """
        Insert a new data stream session.
        :param stream_class: The class name performing the data streaming.
        :param symbol: The symbol associated with the data stream (e.g., 'AAPL').
        :param application_env: The application environment (prod_live, prod_paper, etc.).
        :param start_time: The start time of the data stream session.
        :return: The ID of the newly created session, or -1 if the insertion failed.
        """
        inserted_id = self.insert(
            "insert_data_stream_session.sql",
            (stream_class, symbol, application_env, start_time),
        )
        if not inserted_id:
            self.logger.error(
                f"Failed to insert data stream session for symbol {symbol}."
            )
            return None
        return inserted_id

    def update_data_stream_session_end_time(
        self, session_id: UUID, end_time: datetime
    ) -> int:
        """
        Update the end time of an existing data stream session.
        :param session_id: The ID of the session to update.
        :param end_time: The new end time for the session.
        :return: The number of rows affected by the update.
        """
        update_count = self.update(
            "update_data_stream_session_end_time.sql", (end_time, str(session_id))
        )
        return update_count if update_count else -1

    def delete_all_data_stream_session(self) -> int:
        """
        Delete all data stream sessions.
        :return: The number of rows affected by the delete.
        """
        delete_count = self.delete("delete_all_data_stream_session.sql")
        return delete_count or -1
