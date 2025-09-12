from dependency_injector import containers, providers


class ServicesContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    dao = providers.DependenciesContainer()
    logger = providers.DependenciesContainer()
