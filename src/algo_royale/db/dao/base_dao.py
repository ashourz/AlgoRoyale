# db/dao/base_dao.py
import psycopg2
import logging

class BaseDAO:
    def __init__(self, connection):
        self.conn = connection

    def _execute(self, query, params=None, fetch=False, fetchone=False):
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                elif fetchone:
                    return cur.fetchone()
                self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error: {e}")
            self.conn.rollback()
            raise
