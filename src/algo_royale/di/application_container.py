from dependency_injector import containers, providers

from algo_royale.di.dao_container import DAOContainer
from algo_royale.di.db_container import DBContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.di.repo_container import RepoContainer


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["config.ini"])
    secrets = providers.Configuration(ini_files=["secrets.ini"])
    logger_container = LoggerContainer()

    db_container = providers.Container(DBContainer, config=config, secrets=secrets)

    dao_container = providers.Container(
        DAOContainer,
        config=config,
        db_container=db_container,
        logger_container=logger_container,
    )

    repo_container = providers.Container(
        RepoContainer,
        config=config,
        dao=dao_container,
        logger_container=logger_container,
    )
