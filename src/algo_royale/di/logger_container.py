from dependency_injector import containers, providers

from algo_royale.logging.env_logger_type_dev_integration import (
    EnvLoggerTypeDevIntegration,
)
from algo_royale.logging.env_logger_type_dev_unit import EnvLoggerTypeDevUnit
from algo_royale.logging.env_logger_type_prod_live import EnvLoggerTypeProdLive
from algo_royale.logging.env_logger_type_prod_paper import EnvLoggerTypeProdPaper
from algo_royale.logging.loggable import TaggableLogger
from algo_royale.logging.logger_env import ApplicationEnv
from algo_royale.logging.logger_factory import LoggerFactory
from algo_royale.logging.logger_type import LoggerType


class LoggerContainer(containers.DeclarativeContainer):
    environment = providers.Object(ApplicationEnv)
    logger_factory = providers.Singleton(LoggerFactory, environment=environment)

    def get_logger(self, logger_type: LoggerType):
        if self.environment == ApplicationEnv.PROD_LIVE:
            env_logger_type_enum = EnvLoggerTypeProdLive
        elif self.environment == ApplicationEnv.PROD_PAPER:
            env_logger_type_enum = EnvLoggerTypeProdPaper
        elif self.environment == ApplicationEnv.DEV_UNIT:
            env_logger_type_enum = EnvLoggerTypeDevUnit
        elif self.environment == ApplicationEnv.DEV_INTEGRATION:
            env_logger_type_enum = EnvLoggerTypeDevIntegration
        else:
            raise ValueError(f"Unsupported environment: {self.environment}")
        env_logger_type = getattr(env_logger_type_enum, logger_type.name)
        base_logger = self.logger_factory().get_base_logger()
        return TaggableLogger(base_logger=base_logger, logger_type=env_logger_type)

    logger = providers.DelegatedFactory(
        get_logger,
        logger_type=providers.Dependency(instance_of=LoggerType),
    )


dev_unit_logger_container = LoggerContainer(environment=ApplicationEnv.DEV_UNIT)
dev_integration_logger_container = LoggerContainer(
    environment=ApplicationEnv.DEV_INTEGRATION
)
