from dependency_injector import containers, providers

from algo_royale.clients.db.database import Database
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class DBContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    secrets = providers.Configuration()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    logger = providers.Factory(
        logger_container.logger,
        logger_type=LoggerType.DATABASE,
    )

    database = providers.Singleton(
        Database,
        db_name=config.db.connection.db_name,
        db_user=config.db.connection.db_user,
        db_password=secrets.db.connection.password,
        db_host=config.db.connection.host,
        db_port=config.db.connection.port,
        logger=logger,
    )

    db_connection = providers.Callable(lambda db: db.connection_context(), db=database)

    def run_migrations(self):
        from algo_royale.clients.db.migrations import migration_manager

        db = self.database()
        conn = db.connect(create_if_not_exists=True)
        migration_manager.apply_migrations(conn, logger=self.logger())
        conn.close()
