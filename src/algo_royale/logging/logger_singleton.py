import logging
import os

from algo_royale.logging.custom_rotating_file_handler import CustomRotatingFileHandler
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_type import LoggerType
from algo_royale.utils.path_utils import get_project_root

PROJECT_ROOT = get_project_root()
BASE_LOG_DIR = os.getenv(
    "LOG_DIR", PROJECT_ROOT / "logs"
)  # Use env variable for flexibility


class LoggerSingleton:
    """
    Singleton logger that manages one logger per (module, environment).
    """

    _instances = {}

    @staticmethod
    def get_instance(
        logger_type: LoggerType, environment: LoggerEnv = LoggerEnv.PRODUCTION
    ) -> logging.Logger:
        """
        Get or create a logger instance based on the logger type and environment.
        """
        key = (logger_type, environment)
        if key not in LoggerSingleton._instances:
            base_logger = LoggerSingleton._create_logger(logger_type, environment)
            LoggerSingleton._instances[key] = logging.LoggerAdapter(
                base_logger, {"classname": logger_type.name}
            )
        return LoggerSingleton._instances[key]

    @staticmethod
    def _create_logger(
        logger_type: LoggerType, environment: LoggerEnv
    ) -> logging.Logger:
        """
        Create a new logger instance.
        """
        logger_name = f"{logger_type.name}_{environment.value}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_type.log_level)
        logger.propagate = False

        if not logger.handlers:
            log_dir = os.path.join(BASE_LOG_DIR, environment.value)
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, f"{environment.value}.log")
            file_handler = CustomRotatingFileHandler(
                log_file, maxBytes=10_000_000, backupCount=5
            )
            formatter = logging.Formatter(
                "[%(asctime)s] %(name)s %(levelname)s - %(classname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


def mockLogger() -> logging.Logger:
    """
    Creates a mock logger for testing purposes.
    """
    from algo_royale.logging.logger_env import LoggerEnv
    from algo_royale.logging.logger_type import LoggerType

    logger: logging.Logger = LoggerSingleton.get_instance(
        logger_type=LoggerType.TESTING, environment=LoggerEnv.TEST
    )
    return logger
