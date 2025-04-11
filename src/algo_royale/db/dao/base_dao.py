## db\dao\base_dao.py
import logging
import os

class BaseDAO:
    def __init__(self, connection):
        self.conn = connection

    def _load_sql(self, filename):
        sql_path = os.path.join(os.path.dirname(__file__), '..', 'sql', filename)
        with open(sql_path, 'r') as f:
            return f.read()

    def fetch(self, sql_file, params=None, log_name="fetch"):
        try:
            query = self._load_sql(sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            logging.error(f"[{log_name}] Fetch failed: {e}")
            self.conn.rollback()
            raise

    def fetchone(self, sql_file, params=None, log_name="fetchone"):
        try:
            query = self._load_sql(sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()
        except Exception as e:
            logging.error(f"[{log_name}] FetchOne failed: {e}")
            self.conn.rollback()
            raise

    def insert(self, sql_file, params=None, log_name="insert"):
        try:
            query = self._load_sql(sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            logging.error(f"[{log_name}] Insert failed: {e}")
            self.conn.rollback()
            raise

    def update(self, sql_file, params=None, log_name="update"):
        try:
            query = self._load_sql(sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            logging.error(f"[{log_name}] Update failed: {e}")
            self.conn.rollback()
            raise

    def delete(self, sql_file, params=None, log_name="delete"):
        try:
            query = self._load_sql(sql_file)
            with self.conn.cursor() as cur:
                cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            logging.error(f"[{log_name}] Delete failed: {e}")
            self.conn.rollback()
            raise
