import logging
import os
from enum import Enum
from logging.handlers import RotatingFileHandler

from algo_royale.utils.path_utils import get_project_root


class Environment(Enum):
    PRODUCTION = "production"
    TEST = "test"


class LoggerType(Enum):
    """
    Enum defining logger types for each module, with logging levels.
    """

    TRADING = ("trading", logging.INFO)
    BACKTESTING = ("backtesting", logging.DEBUG)
    WATCHLIST = ("watchlist", logging.INFO)

    def __init__(self, log_name: str, log_level: int):
        self.log_name = log_name
        self.log_level = log_level


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
        logger_type: LoggerType, environment: Environment = Environment.PRODUCTION
    ) -> logging.Logger:
        """
        Get or create a logger instance based on the logger type and environment.
        """
        key = (logger_type, environment)
        if key not in LoggerSingleton._instances:
            LoggerSingleton._instances[key] = LoggerSingleton._create_logger(
                logger_type, environment
            )
        return LoggerSingleton._instances[key]

    @staticmethod
    def _create_logger(
        logger_type: LoggerType, environment: Environment
    ) -> logging.Logger:
        """
        Create a new logger instance.
        """
        logger_name = f"{logger_type.log_name}_{environment.value}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_type.log_level)
        logger.propagate = False

        if not logger.handlers:
            log_dir = os.path.join(BASE_LOG_DIR, environment.value)
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, f"{logger_type.log_name}.log")
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10_000_000, backupCount=5
            )
            formatter = logging.Formatter(
                "[%(asctime)s] %(name)s %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger
