from dependency_injector import containers, providers

from algo_royale.logging.env_logger_type_integration import EnvLoggerTypeIntegration
from algo_royale.logging.env_logger_type_prod import EnvLoggerTypeProd
from algo_royale.logging.env_logger_type_test import EnvLoggerTypeTest
from algo_royale.logging.env_logger_type_unit import EnvLoggerTypeUnit
from algo_royale.logging.loggable import TaggableLogger
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_factory import LoggerFactory
from algo_royale.logging.logger_type import LoggerType


class LoggerContainer(containers.DeclarativeContainer):
    environment = providers.Object(LoggerEnv)
    base_logger_backtest = providers.Singleton(
        LoggerFactory.get_base_logger, environment=environment
    )

    @staticmethod
    def get_env_logger_type(environment: LoggerEnv):
        if environment == LoggerEnv.UNIT:
            return EnvLoggerTypeUnit
        elif environment == LoggerEnv.INTEGRATION:
            return EnvLoggerTypeIntegration
        elif environment == LoggerEnv.TEST:
            return EnvLoggerTypeTest
        elif environment == LoggerEnv.PROD:
            return EnvLoggerTypeProd
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


unit_logger_container = LoggerContainer(environment=LoggerEnv.UNIT)
integration_logger_container = LoggerContainer(environment=LoggerEnv.INTEGRATION)
