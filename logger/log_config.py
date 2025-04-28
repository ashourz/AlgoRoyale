# log_config.py

import logging
import os
from enum import Enum
from logging.handlers import RotatingFileHandler

"""
# Explicitly getting test logger
test_logger = get_logger(LoggerType.TEST)
test_logger.debug("Running tests...")

# Explicitly getting integration logger
integration_logger = get_logger(LoggerType.INTEGRATION)
integration_logger.info("Running integration tests...")

# Implicitly getting prod logger (no argument)
prod_logger = get_logger()
prod_logger.warning("Running in production!")
"""

# Step 1: Enum with logging level as a parameter
class LoggerType(Enum):
    TEST = ("test", logging.DEBUG)
    INTEGRATION = ("integration", logging.INFO)
    PROD = ("prod", logging.WARNING)

    def __init__(self, log_name: str, log_level: int):
        self.log_name = log_name
        self.log_level = log_level

# Step 2: Figure out log folder
BASE_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# Step 3: Auto-setup logger
def setup_logger(logger_type: LoggerType) -> logging.Logger:
    logger = logging.getLogger(logger_type.log_name)
    logger.setLevel(logger_type.log_level)
    logger.propagate = False

    if not logger.handlers:  # Prevent duplicate handlers
        log_file = os.path.join(BASE_LOG_DIR, f"{logger_type.log_name}.log")
        file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Step 4: Pre-create all loggers
LOGGER_MAP = {logger_type: setup_logger(logger_type) for logger_type in LoggerType}

# Step 5: Easy getter
def get_logger(logger_type: LoggerType = LoggerType.PROD) -> logging.Logger:
    return LOGGER_MAP[logger_type]
