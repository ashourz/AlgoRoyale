from algo_royale.clients.db.database import Database
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class DBContainer:
    def __init__(self, config, secrets, logger_container: LoggerContainer):
        self.config = config
        self.secrets = secrets
        self.logger_container = logger_container
        self.logger = self.logger_container.logger(logger_type=LoggerType.DATABASE)
        self.database = Database(
            db_name=self.config["db_connection"]["db_name"],
            db_user=self.config["db_connection"]["db_user"],
            db_password=self.secrets["db_connection"]["password"],
            db_host=self.config["db_connection"]["host"],
            db_port=int(self.config["db_connection"]["port"]),
            logger=self.logger,
        )

    @property
    def db_connection(self, create_if_not_exists=False):
        try:
            if (
                not hasattr(self, "_shared_connection")
                or self._shared_connection is None
                or self._shared_connection.closed
            ):
                self._shared_connection = self.database.connect(
                    create_if_not_exists=create_if_not_exists
                )
            return self._shared_connection
        except Exception as e:
            self.logger.error(f"Error getting DB connection: {e}")
            raise e

    def close(self):
        try:
            if (
                hasattr(self, "_shared_connection")
                and self._shared_connection
                and not self._shared_connection.closed
            ):
                self._shared_connection.close()
        except Exception as e:
            self.logger.error(f"Error closing DB connection: {e}")

    def run_migrations(self):
        try:
            from algo_royale.clients.db.migrations import migration_manager

            db = self.database
            conn = db.connect(create_if_not_exists=True)
            migration_manager.apply_migrations(conn, logger=self.logger)
            conn.close()
        except Exception as e:
            self.logger.error(f"Error running migrations: {e}")
            raise e
