from dependency_injector import containers, providers

from algo_royale.logging.loggable import TaggableLogger
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_factory import LoggerFactory
from algo_royale.logging.logger_type import LoggerType


class LoggerContainer(containers.DeclarativeContainer):
    base_logger_backtest = providers.Singleton(
        LoggerFactory.get_base_logger, environment=LoggerEnv.BACKTEST
    )

    def provides_logger(self, logger_type: LoggerType):
        provider = providers.Factory(
            TaggableLogger,
            base_logger=self.base_logger_backtest(),
            logger_type=logger_type,
        )
        return provider()
