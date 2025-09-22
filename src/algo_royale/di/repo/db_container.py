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
    def db_connection(self):
        return self.database.connection_context()

    def run_migrations(self):
        from algo_royale.clients.db.migrations import migration_manager

        db = self.database
        conn = db.connect(create_if_not_exists=True)
        migration_manager.apply_migrations(conn, logger=self.logger)
        conn.close()
