from dependency_injector import containers, providers

from algo_royale.logging.loggable import TaggableLogger
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_factory import LoggerFactory
from algo_royale.logging.logger_type import LoggerType


class LoggerContainer(containers.DeclarativeContainer):
    base_logger_backtest = providers.Singleton(
        LoggerFactory.get_base_logger, environment=LoggerEnv.BACKTEST
    )

    logger_trading = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.TRADING,
    )

    logger_stage_data_manager = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STAGE_DATA_MANAGER,
    )

    logger_stage_data_preparer = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STAGE_DATA_PREPARER,
    )

    logger_stage_data_writer = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STAGE_DATA_WRITER,
    )
    logger_stage_data_loader = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STAGE_DATA_LOADER,
    )

    logger_symbol_strategy_data_loader = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STRATEGY_DATA_LOADER,
    )
    logger_symbol_strategy_data_writer = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STRATEGY_DATA_WRITER,
    )

    logger_strategy_executor = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STRATEGY_EXECUTOR,
    )

    logger_strategy_evaluator = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STRATEGY_EVALUATOR,
    )
    logger_strategy_factory = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STRATEGY_FACTORY,
    )
    logger_signal_strategy_optimizer = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.SIGNAL_STRATEGY_OPTIMIZER,
    )
    logger_portfolio_executor = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_EXECUTOR,
    )
    logger_portfolio_evaluator = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_EVALUATOR,
    )
    logger_portfolio_asset_matrix_preparer = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_ASSET_MATRIX_PREPARER,
    )
    logger_portfolio_matrix_loader = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_MATRIX_LOADER,
    )
    logger_portfolio_strategy_optimizer = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_STRATEGY_OPTIMIZER,
    )
    logger_strategy_evaluation = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STRATEGY_EVALUATION,
    )
    logger_symbol_evaluation = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.SYMBOL_EVALUATION,
    )
    logger_portfolio_evaluation = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_EVALUATION,
    )
    logger_backtest_data_ingest = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.BACKTEST_DATA_INGEST,
    )
    logger_backtest_feature_engineering = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.BACKTEST_FEATURE_ENGINEERING,
    )
    logger_backtest_signal_optimization = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.BACKTEST_SIGNAL_OPTIMIZATION,
    )
    logger_backtest_signal_testing = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.BACKTEST_SIGNAL_TESTING,
    )
    logger_backtest_portfolio_optimization = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.BACKTEST_PORTFOLIO_OPTIMIZATION,
    )
    logger_backtest_portfolio_testing = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.BACKTEST_PORTFOLIO_TESTING,
    )
    logger_symbol_strategy_manager = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.SYMBOL_STRATEGY_MANAGER,
    )
    logger_strategy_walk_forward = providers.Factory(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.STRATEGY_WALK_FORWARD,
    )
    logger_portfolio_walk_forward = providers.Singleton(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_WALK_FORWARD,
    )
    logger_backtest_pipeline = providers.Singleton(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.BACKTEST_PIPELINE,
    )
    logger_signal_strategy = providers.Singleton(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.SIGNAL_STRATEGY,
    )
    logger_portfolio_strategy = providers.Singleton(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_STRATEGY,
    )
    logger_signal_strategy_combinator_factory = providers.Singleton(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.SIGNAL_STRATEGY_COMBINATOR_FACTORY,
    )
    logger_portfolio_strategy_combinator_factory = providers.Singleton(
        TaggableLogger,
        base_logger=base_logger_backtest,
        logger_type=LoggerType.PORTFOLIO_STRATEGY_COMBINATOR_FACTORY,
    )
