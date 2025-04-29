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


