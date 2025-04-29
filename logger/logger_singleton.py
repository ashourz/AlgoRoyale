from enum import Enum
import logging
from logging.handlers import RotatingFileHandler
import os


# Step 1: Enum with logging level as a parameter for different modules
class LoggerType(Enum):
    """
    Enum that defines different logger types for different application modules 
    with corresponding logging levels.

    Attributes:
        TEST: Logging level DEBUG for test environments.
        INTEGRATION: Logging level INFO for integration environments.
        TRADING: Logging level INFO for the trading module.
        BACKTESTING: Logging level DEBUG for the backtesting module.
        WATCHLIST: Logging level INFO for the watchlist/scout module.
    """
    TEST = ("test", logging.DEBUG)
    INTEGRATION = ("integration", logging.INFO)
    TRADING = ("trading", logging.INFO)
    BACKTESTING = ("backtesting", logging.DEBUG)
    WATCHLIST = ("watchlist", logging.INFO)

    def __init__(self, log_name: str, log_level: int):
        self.log_name = log_name  # The name of the logger
        self.log_level = log_level  # The logging level for the logger


# Step 2: Setup log folder
BASE_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(BASE_LOG_DIR, exist_ok=True)

def _setup_logger(logger_type: LoggerType) -> logging.Logger:
    """
    Set up the logger with rotating file handler and specified log level.

    Args:
        logger_type (LoggerType): The logger type (e.g., TEST, INTEGRATION, TRADING, etc.)

    Returns:
        logging.Logger: Configured logger for the given environment/module.
    """
    logger = logging.getLogger(logger_type.log_name)
    logger.setLevel(logger_type.log_level)
    logger.propagate = False  # Prevent propagation of log messages to the root logger

    # Check if the logger has handlers already, to avoid adding duplicates
    if not logger.handlers:
        log_file = os.path.join(BASE_LOG_DIR, f"{logger_type.log_name}.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Step 3: Pre-create all loggers for each environment/module
LOGGER_MAP = {logger_type: _setup_logger(logger_type) for logger_type in LoggerType}

def _get_logger(logger_type: LoggerType = LoggerType.TRADING) -> logging.Logger:
    """
    Retrieve the logger for a specific environment/module.

    Args:
        logger_type (LoggerType, optional): The logger type (default is TRADING). 

    Returns:
        logging.Logger: The logger associated with the specified environment/module.
    """
    return LOGGER_MAP[logger_type]

class LoggerSingleton:
    """
    Singleton class for managing and reusing logger instances across different application modules.

    This class ensures that only one logger instance exists for each module (e.g., trading, backtesting, 
    watchlist, etc.) to avoid unnecessary re-initialization. It also allows switching the module dynamically.

    # Usage Example:
    # logger = LoggerSingleton().get_logger(module='trading')  # For trading logs
    # logger = LoggerSingleton().get_logger(module='backtesting')  # For backtesting logs
    # logger = LoggerSingleton().get_logger(module='watchlist')  # For watchlist logs
    
    The logger is initialized based on the module passed, or defaults to 'prod' 
    if no module is specified. Once initialized, the same logger instance will 
    be used throughout the lifetime of the application.
    """

    _instance = None  # Single instance of the LoggerSingleton
    
    def __new__(cls, *args, **kwargs):
        """
        Create or return the existing instance of LoggerSingleton.
        
        Ensures only one instance of the singleton is created.
        """
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance.logger = None  # Initially no logger instance
        return cls._instance

    def get_logger(self, logger_type: LoggerType = LoggerType.TRADING):
        """
        Retrieve the logger instance for the specified environment/module.

        This method ensures that if the logger is already initialized, the existing 
        logger will be returned. If the logger isn't initialized, it will be created 
        for the given environment/module.

        Args:
            logger_type (LoggerType, optional): The environment/module to get the logger for 
                                                  (default is PROD).

        Returns:
            logging.Logger: The logger for the specified environment/module.

        Raises:
            ValueError: If an invalid logger type is passed.
        """
        # If logger already initialized, return the existing one
        if self.logger is not None:
            return self.logger

        # Check if logger_type is valid and initialize logger
        if logger_type not in LoggerType:
            raise ValueError(f"Invalid logger type: {logger_type}")
        
        # Initialize the logger based on the environment/module
        self.logger = _get_logger(logger_type)

        return self.logger
