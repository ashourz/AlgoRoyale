## db\dao\base_dao.py
from logging import Logger
import os
import psycopg2


class BaseDAO:
    def __init__(self, 
                 connection: psycopg2.extensions.connection, 
                 sql_dir: str,
                 logger: Logger):
        self.conn = connection
        self.sql_dir = sql_dir
        self.logger = logger

    def _load_sql(self, sql_file: str):
        sql_path = os.path.join(self.sql_dir, sql_file)
        with open(sql_path, 'r') as f:
            return f.read()

    def fetch(self, sql_file: str, params=None, log_name="fetch"):
        try:
            query = self._load_sql(sql_file = sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            self.logger.error(f"[{log_name}] Fetch failed: {e}")
            self.conn.rollback()
            raise

    def fetchone(self, sql_file: str, params=None, log_name="fetchone"):
        try:
            query = self._load_sql(sql_file = sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()
        except Exception as e:
            self.logger.error(f"[{log_name}] FetchOne failed: {e}")
            self.conn.rollback()
            raise

    def insert(self, sql_file: str, params=None, log_name="insert"):
        try:
            query = self._load_sql(sql_file = sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"[{log_name}] Insert failed: {e}")
            self.conn.rollback()
            raise

    def update(self, sql_file: str, params=None, log_name="update"):
        try:
            query = self._load_sql(sql_file = sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"[{log_name}] Update failed: {e}")
            self.conn.rollback()
            raise

    def delete(self, sql_file: str, params=None, log_name="delete"):
        try:
            query = self._load_sql(sql_file = sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            self.logger.error(f"[{log_name}] Delete failed: {e}")
            self.conn.rollback()
            raise