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
    base_logger_backtest = providers.Singleton(
        LoggerFactory.get_base_logger, environment=environment
    )

    @staticmethod
    def get_env_logger_type(environment: ApplicationEnv):
        if environment == ApplicationEnv.PROD_LIVE:
            return EnvLoggerTypeProdLive
        elif environment == ApplicationEnv.PROD_PAPER:
            return EnvLoggerTypeProdPaper
        elif environment == ApplicationEnv.DEV_INTEGRATION:
            return EnvLoggerTypeDevUnit
        elif environment == ApplicationEnv.DEV_INTEGRATION:
            return EnvLoggerTypeDevIntegration
        else:
            raise ValueError(f"Unsupported environment: {environment}")

    logger_type = providers.Factory(get_env_logger_type, environment=environment)

    def provides_logger(self, logger_type: LoggerType):
        env_logger_type_enum = self.logger_type()
        env_logger_type = getattr(env_logger_type_enum, logger_type.name)
        provider = providers.Factory(
            TaggableLogger,
            base_logger=self.base_logger_backtest(),
            logger_type=env_logger_type,
        )
        return provider()


dev_unit_logger_container = LoggerContainer(environment=ApplicationEnv.DEV_UNIT)
dev_integration_logger_container = LoggerContainer(
    environment=ApplicationEnv.DEV_INTEGRATION
)
