import logging
import os

from algo_royale.logging.custom_rotating_file_handler import CustomRotatingFileHandler
from algo_royale.logging.loggable import Loggable
from algo_royale.utils.application_env import ApplicationEnv
from algo_royale.utils.path_utils import get_project_root

PROJECT_ROOT = get_project_root()
BASE_LOG_DIR = os.getenv("LOG_DIR", PROJECT_ROOT / "logs")


class TaggedLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # `kwargs` may be None (logging API sometimes passes None).
        # Also `kwargs.get("extra")` may be None. Normalize both to dicts
        # so we can safely subscript them without triggering Pylance warnings.
        if kwargs is None:
            kwargs = {}

        extra = kwargs.get("extra")
        if extra is None:
            extra = {}
            kwargs["extra"] = extra

        # `self.extra` is provided when the adapter is created. Be defensive
        # in case it's not a dict (tests or callers may pass an object).
        tag = None
        if isinstance(self.extra, dict):
            tag = self.extra.get("tag")
        else:
            tag = getattr(self.extra, "tag", None)

        extra["tag"] = tag
        return msg, kwargs


class LoggerFactory:
    def __init__(self, environment: ApplicationEnv):
        self.environment = environment
        self._loggers = {}

    def get_base_logger(self) -> logging.Logger:
        logger_name = self.environment.value
        if logger_name in self._loggers:
            return self._loggers[logger_name]

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)  # Allow all logs, filter in wrapper
        logger.propagate = False

        log_dir = os.path.join(BASE_LOG_DIR, self.environment.value)
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, f"{self.environment.value}.log")

        # Only add a handler if none exist to prevent duplicate logs
        if not logger.hasHandlers():
            file_handler = CustomRotatingFileHandler(
                log_file, maxBytes=10_000_000, backupCount=100, encoding="utf-8"
            )
            formatter = logging.Formatter(
                "[%(asctime)s] %(name)s %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        self._loggers[logger_name] = logger
        return logger


def mockLogger() -> logging.Logger:
    """
    Creates a mock logger for testing purposes.
    """
    from algo_royale.utils.application_env import ApplicationEnv

    logger: Loggable = LoggerFactory(ApplicationEnv.DEV_UNIT).get_base_logger()
    return logger
