import logging
from enum import Enum


class LoggerType(Enum):
    """
    Enum defining logger types for each module, with logging levels.
    """

    TRADING = logging.INFO

    STAGE_DATA_MANAGER = logging.DEBUG
    STAGE_DATA_PREPARER = logging.DEBUG
    STAGE_DATA_WRITER = logging.DEBUG
    STAGE_DATA_LOADER = logging.DEBUG

    STRATEGY_DATA_LOADER = logging.DEBUG
    STRATEGY_DATA_WRITER = logging.DEBUG

    STRATEGY_EXECUTOR = logging.DEBUG
    STRATEGY_EVALUATOR = logging.DEBUG
    STRATEGY_FACTORY = logging.DEBUG

    SIGNAL_STRATEGY_OPTIMIZER = logging.DEBUG

    PORTFOLIO_EXECUTOR = logging.DEBUG
    PORTFOLIO_EVALUATOR = logging.DEBUG

    PORTFOLIO_ASSET_MATRIX_PREPARER = logging.DEBUG
    PORTFOLIO_STRATEGY_OPTIMIZER = logging.DEBUG

    STRATEGY_EVALUATION = logging.DEBUG
    SYMBOL_EVALUATION = logging.DEBUG
    PORTFOLIO_EVALUATION = logging.DEBUG

    BACKTEST_DATA_INGEST = logging.DEBUG
    BACKTEST_FEATURE_ENGINEERING = logging.DEBUG
    BACKTEST_SIGNAL_OPTIMIZATION = logging.DEBUG
    BACKTEST_SIGNAL_TESTING = logging.DEBUG
    BACKTEST_PORTFOLIO_OPTIMIZATION = logging.DEBUG
    BACKTEST_PORTFOLIO_TESTING = logging.DEBUG

    STRATEGY_WALK_FORWARD = logging.DEBUG
    PORTFOLIO_WALK_FORWARD = logging.DEBUG

    BACKTEST_PIPELINE = logging.DEBUG

    WATCHLIST = logging.DEBUG
    TESTING = logging.DEBUG

    @property
    def log_level(self):
        return self.value
