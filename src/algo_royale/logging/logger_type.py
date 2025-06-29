import logging
from enum import Enum


class LoggerType(Enum):
    """
    Enum defining logger types for each module, with logging levels.
    """

    TRADING = ("trading", logging.INFO)
    BACKTESTING = ("backtesting", logging.WARNING)
    WATCHLIST = ("watchlist", logging.INFO)
    TESTING = ("testing", logging.NOTSET)

    @property
    def log_name(self):
        return self.value[0]

    @property
    def log_level(self):
        return self.value[1]
