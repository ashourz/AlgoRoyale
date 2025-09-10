from dependency_injector import containers, providers

from algo_royale.clients.db.database import Database


class DBContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    secrets = providers.Configuration()

    database = providers.Singleton(
        Database,
        db_name=config.db.connection.dbname,
        db_user=config.db.connection.user,
        db_password=secrets.db.connection.password,
        db_host=config.db.connection.host,
        db_port=config.db.connection.port,
        logger=config.logger_trading,
    )

    db_connection = providers.Callable(lambda db: db.connection_context(), db=database)
