from enum import Enum
import logging
from logging.handlers import RotatingFileHandler
import os


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


BASE_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")


class LoggerSingleton:
    """
    Singleton logger that manages one logger per (module, environment).
    """
    _instances = {}

    def __new__(cls, module: LoggerType, env: Environment = Environment.PRODUCTION):
        key = (module, env)
        if key not in cls._instances:
            instance = super().__new__(cls)
            instance._initialize_logger(module, env)
            cls._instances[key] = instance
        return cls._instances[key]

    def _initialize_logger(self, module: LoggerType, env: Environment):
        logger_name = f"{module.log_name}_{env.value}"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(module.log_level)
        self.logger.propagate = False

        if not self.logger.handlers:
            log_dir = os.path.join(BASE_LOG_DIR, env.value)
            os.makedirs(log_dir, exist_ok=True)

            log_file = os.path.join(log_dir, f"{module.log_name}.log")
            file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger
