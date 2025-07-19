# algo_royale/logging/loggable.py

import logging
from typing import Protocol, runtime_checkable

from algo_royale.logging.logger_type import LoggerType


@runtime_checkable
class Loggable(Protocol):
    def debug(self, msg: str, *args, **kwargs): ...
    def info(self, msg: str, *args, **kwargs): ...
    def warning(self, msg: str, *args, **kwargs): ...
    def error(self, msg: str, *args, **kwargs): ...
    def critical(self, msg: str, *args, **kwargs): ...
    def exception(self, msg: str, *args, **kwargs): ...


class TaggableLogger(Loggable):
    def __init__(self, base_logger: logging.Logger, logger_type: LoggerType):
        self._logger = base_logger
        self._logger_type = logger_type
        self._log_level = logger_type.log_level
        self._tag = logger_type.name_str

    def _should_log(self, level):
        return level >= self._log_level

    def _log(self, level, msg, *args, **kwargs):
        if self._should_log(level):
            tagged_msg = f"{self._tag} - {msg}"
            self._logger.log(level, tagged_msg, *args, **kwargs)
            if self._logger_type.print_logs:
                print(tagged_msg)

    def debug(self, msg, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, exc_info=True, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)
