import logging
from enum import Enum


class LoggerType(Enum):
    """
    Enum defining logger types for each module, with logging levels.
    """

    TRADING = ("trading", logging.INFO)

    STAGE_DATA_MANAGER = ("stage_data_manager", logging.DEBUG)
    STAGE_DATA_PREPARER = ("stage_data_preparer", logging.DEBUG)
    STAGE_DATA_WRITER = ("stage_data_writer", logging.DEBUG)
    STAGE_DATA_LOADER = ("stage_data_loader", logging.DEBUG)

    STRATEGY_DATA_LOADER = ("strategy_data_loader", logging.DEBUG)
    STRATEGY_DATA_WRITER = ("strategy_data_writer", logging.DEBUG)

    STRATEGY_EXECUTOR = ("strategy_executor", logging.DEBUG)
    STRATEGY_EVALUATOR = ("strategy_evaluator", logging.DEBUG)
    STRATEGY_FACTORY = ("strategy_factory", logging.DEBUG)

    SIGNAL_STRATEGY_OPTIMIZER = ("signal_strategy_optimizer", logging.DEBUG)

    PORTFOLIO_EXECUTOR = ("portfolio_executor", logging.DEBUG)
    PORTFOLIO_EVALUATOR = ("portfolio_evaluator", logging.DEBUG)

    PORTFOLIO_ASSET_MATRIX_PREPARER = ("portfolio_asset_matrix_preparer", logging.DEBUG)
    PORTFOLIO_STRATEGY_OPTIMIZER = ("portfolio_strategy_optimizer", logging.DEBUG)

    STRATEGY_EVALUATION = ("strategy_evaluation", logging.DEBUG)
    SYMBOL_EVALUATION = ("symbol_evaluation", logging.DEBUG)
    PORTFOLIO_EVALUATION = ("portfolio_evaluation", logging.DEBUG)

    BACKTEST_DATA_INGEST = ("backtest_data", logging.DEBUG)
    BACKTEST_FEATURE_ENGINEERING = ("backtest_feature_engineering", logging.DEBUG)
    BACKTEST_SIGNAL_OPTIMIZATION = ("backtest_signal_optimization", logging.DEBUG)
    BACKTEST_SIGNAL_TESTING = ("backtest_signal_testing", logging.DEBUG)
    BACKTEST_PORTFOLIO_OPTIMIZATION = ("backtest_portfolio_optimization", logging.DEBUG)
    BACKTEST_PORTFOLIO_TESTING = ("backtest_portfolio_testing", logging.DEBUG)

    STRATEGY_WALK_FORWARD = ("strategy_walk_forward", logging.DEBUG)
    PORTFOLIO_WALK_FORWARD = ("portfolio_walk_forward", logging.DEBUG)

    BACKTEST_PIPELINE = ("backtest_pipeline", logging.DEBUG)

    WATCHLIST = ("watchlist", logging.DEBUG)
    TESTING = ("testing", logging.DEBUG)

    @property
    def log_name(self):
        return self.value[0]

    @property
    def log_level(self):
        return self.value[1]
