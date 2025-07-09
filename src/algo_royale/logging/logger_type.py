import logging
from enum import Enum


class LoggerType(Enum):
    """
    Enum defining logger types for each module, with logging levels.
    """

    TRADING = ("trading", logging.INFO)
    BACKTESTING = ("backtesting", logging.DEBUG)
    WATCHLIST = ("watchlist", logging.DEBUG)
    TESTING = ("testing", logging.DEBUG)

    @property
    def log_name(self):
        return self.value[0]

    @property
    def log_level(self):
        return self.value[1]
