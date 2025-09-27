from algo_royale.clients.db.database import Database
from algo_royale.clients.db.database_admin import DatabaseAdmin
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class DBContainer:
    def __init__(self, config, secrets, logger_container: LoggerContainer):
        self.config = config
        self.secrets = secrets
        self.logger_container = logger_container
        self.logger = self.logger_container.logger(logger_type=LoggerType.DATABASE)

    @property
    def database_admin(self) -> DatabaseAdmin:
        return DatabaseAdmin(
            master_db_name=self.config["db_master_connection"]["db_name"],
            master_db_user=self.config["db_master_connection"]["db_user"],
            master_db_password=self.secrets["db_master_connection"]["password"],
            db_host=self.config["db_connection"]["host"],
            db_port=int(self.config["db_connection"]["port"]),
            logger=self.logger,
        )

    @property
    def database(self) -> Database:
        return Database(
            database_admin=self.database_admin,
            db_name=self.config["db_connection"]["db_name"],
            db_user=self.config["db_connection"]["db_user"],
            db_password=self.secrets["db_connection"]["password"],
            logger=self.logger,
        )

    def setup_environment(self):
        try:
            self.logger.info("🔧 Setting up database environment...")
            self.database_admin.setup_environment(
                db_name=self.config["db_connection"]["db_name"],
                db_user=self.config["db_connection"]["db_user"],
                db_password=self.secrets["db_connection"]["password"],
            )
        except Exception as e:
            self.logger.error(f"Error setting up database environment: {e}")
            raise e

    def teardown_environment(self):
        try:
            self.logger.info("🧹 Tearing down database environment...")
            self.database_admin.user_manager.delete_user(
                username=self.config["db_connection"]["db_user"]
            )
            self.database_admin.database_manager.drop_database(
                master_db_connection=self.database_admin.get_master_db_connection(),
                db_name=self.config["db_connection"]["db_name"],
            )
        except Exception as e:
            self.logger.error(f"Error tearing down database environment: {e}")
            raise e

    @property
    def db_connection(self):
        self.logger.debug(
            f"db_connection property accessed with user={self.config['db_connection']['db_user']} db={self.config['db_connection']['db_name']}"
        )
        try:
            if (
                not hasattr(self, "_shared_connection")
                or self._shared_connection is None
                or self._shared_connection.closed
            ):
                self.logger.info("🔗 Establishing new DB connection...")
                self._shared_connection = self.database.connect()
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
                self.logger.info("🔒 Closing DB connection...")
                self._shared_connection.close()
        except Exception as e:
            self.logger.error(f"Error closing DB connection: {e}")
