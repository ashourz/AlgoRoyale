import logging
import os

from algo_royale.logging.custom_rotating_file_handler import CustomRotatingFileHandler
from algo_royale.logging.loggable import Loggable
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_type import LoggerType
from algo_royale.utils.path_utils import get_project_root

PROJECT_ROOT = get_project_root()
BASE_LOG_DIR = os.getenv("LOG_DIR", PROJECT_ROOT / "logs")


class TaggedLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"]["tag"] = self.extra["tag"]
        return msg, kwargs


class LoggerFactory:
    _loggers = {}

    @staticmethod
    def get_base_logger(environment: LoggerEnv = LoggerEnv.BACKTEST) -> logging.Logger:
        logger_name = environment.value
        if logger_name in LoggerFactory._loggers:
            return LoggerFactory._loggers[logger_name]

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)  # Allow all logs, filter in wrapper
        logger.propagate = False

        log_dir = os.path.join(BASE_LOG_DIR, environment.value)
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"{environment.value}.log")
        file_handler = CustomRotatingFileHandler(
            log_file, maxBytes=10_000_000, backupCount=5
        )
        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        LoggerFactory._loggers[logger_name] = logger
        return logger


def mockLogger() -> logging.Logger:
    """
    Creates a mock logger for testing purposes.
    """
    from algo_royale.logging.logger_env import LoggerEnv

    logger: Loggable = LoggerFactory.get_base_logger(
        logger_type=LoggerType.TESTING, environment=LoggerEnv.TEST
    )
    return logger
