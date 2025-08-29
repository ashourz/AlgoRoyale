from dependency_injector import containers, providers

from algo_royale.di.config_container import ConfigContainer


class DBContainer(containers.DeclarativeContainer):
    def __init__(self, config_container: ConfigContainer):
        self.config_container = config_container

    dao_sql_dir = providers.Callable(
        lambda config: config.get("paths.db", "sql_dir"),
        config=self.config_container.config,
    )
