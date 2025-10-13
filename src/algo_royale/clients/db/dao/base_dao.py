## db\dao\base_dao.py
import os
from uuid import UUID

import psycopg2

from algo_royale.logging.loggable import Loggable


class BaseDAO:
    def __init__(
        self, connection: psycopg2.extensions.connection, sql_dir: str, logger: Loggable
    ):
        self.conn = connection
        self.sql_dir = sql_dir
        self.logger = logger

    def _load_sql(self, sql_file: str):
        sql_path = os.path.join(self.sql_dir, sql_file)
        with open(sql_path, "r") as f:
            return f.read()

    def fetch(self, sql_file: str, params=None, log_name="fetch") -> list:
        """
        Fetch multiple records from the database.
        :param sql_file: The SQL file containing the fetch query.
        :param params: The parameters to include in the query.
        :param log_name: The name to use for logging.
        :return: A list of tuples containing the record data, or an empty list if not found.
        """
        try:
            query = self._load_sql(sql_file=sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            self.logger.error(f"[{log_name}] Fetch failed: {e}")
            self.conn.rollback()
            raise

    def fetchone(self, sql_file: str, params=None, log_name="fetchone") -> tuple:
        """
        Fetch a single record from the database.
        :param sql_file: The SQL file containing the fetchone query.
        :param params: The parameters to include in the query.
        :param log_name: The name to use for logging.
        :return: A tuple containing the record data, or None if not found.
        """
        try:
            query = self._load_sql(sql_file=sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()
        except Exception as e:
            self.logger.error(f"[{log_name}] FetchOne failed: {e}")
            self.conn.rollback()
            raise

    def insert(self, sql_file: str, params=None, log_name="insert") -> UUID | None:
        """
        Insert a new record into the database.
        :param sql_file: The SQL file containing the insert query.
        :param params: The parameters to include in the query.
        :return: The ID of the newly created record, or -1 if the insertion failed.
        """
        try:
            result = None
            query = self._load_sql(sql_file=sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchone()
            self.conn.commit()
            return result[0] if result else None
        except Exception as e:
            self.logger.error(f"[{log_name}] Insert failed: {e}")
            self.conn.rollback()
            raise

    def update(self, sql_file: str, params=None, log_name="update") -> int:
        """
        Update a record in the database.
        :param sql_file: The SQL file containing the update query.
        :param params: The parameters to include in the query.
        :param log_name: The name to use for logging.
        :return: The number of rows affected by the update.
        """
        try:
            result = None
            query = self._load_sql(sql_file=sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.rowcount
            self.conn.commit()
            return result
        except Exception as e:
            self.logger.error(f"[{log_name}] Update failed: {e}")
            self.conn.rollback()
            raise

    def delete(self, sql_file: str, params=None, log_name="delete") -> int:
        """
        Delete a record from the database.
        :param sql_file: The SQL file containing the delete query.
        :param params: The parameters to include in the query.
        :param log_name: The name to use for logging.
        :return: The number of rows affected by the delete.
        """
        try:
            result = None
            query = self._load_sql(sql_file=sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.rowcount
            self.conn.commit()
            return result
        except Exception as e:
            self.logger.error(f"[{log_name}] Delete failed: {e}")
            self.conn.rollback()
            raise
