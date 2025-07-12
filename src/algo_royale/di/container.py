from functools import partial

from dependency_injector import containers, providers

from algo_royale.backtester.data_preparer.asset_matrix_preparer import (
    AssetMatrixPreparer,
)
from algo_royale.backtester.data_preparer.stage_data_preparer import StageDataPreparer
from algo_royale.backtester.evaluator.backtest.portfolio_backtest_evaluator import (
    PortfolioBacktestEvaluator,
)
from algo_royale.backtester.evaluator.backtest.signal_backtest_evaluator import (
    SignalBacktestEvaluator,
)
from algo_royale.backtester.evaluator.portfolio.portfolio_evaluation_coordinator import (
    PortfolioEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.strategy.strategy_evaluation_coordinator import (
    StrategyEvaluationCoordinator,
)
from algo_royale.backtester.evaluator.strategy.strategy_evaluation_type import (
    StrategyEvaluationType,
)
from algo_royale.backtester.evaluator.symbol.symbol_evaluation_coordinator import (
    SymbolEvaluationCoordinator,
)
from algo_royale.backtester.executor.portfolio_backtest_executor import (
    PortfolioBacktestExecutor,
)
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer
from algo_royale.backtester.feature_engineering.feature_engineering import (
    feature_engineering,
)
from algo_royale.backtester.optimizer.portfolio.portfolio_strategy_optimizer_factory import (
    PortfolioStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.optimizer.signal.signal_strategy_optimizer_factory import (
    SignalStrategyOptimizerFactoryImpl,
)
from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.backtester.stage_coordinator.data_staging.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.data_staging.feature_engineering_stage_coordinator import (
    FeatureEngineeringStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.optimization.portfolio_optimization_stage_coordinator import (
    PortfolioOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.optimization.strategy_optimization_stage_coordinator import (
    StrategyOptimizationStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.portfolio_testing_stage_coordinator import (
    PortfolioTestingStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.testing.strategy_testing_stage_coordinator import (
    StrategyTestingStageCoordinator,
)
from algo_royale.backtester.stage_data.loader.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.loader.symbol_strategy_data_loader import (
    SymbolStrategyDataLoader,
)
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.writer.stage_data_writer import StageDataWriter
from algo_royale.backtester.stage_data.writer.symbol_strategy_data_writer import (
    SymbolStrategyDataWriter,
)
from algo_royale.backtester.strategy_combinator.portfolio.equal_risk_contribution_portfolio_strategy_combinator import (
    EqualRiskContributionPortfolioStrategyCombinator,
)
from algo_royale.backtester.strategy_combinator.signal.bollinger_bands_strategy_combinator import (
    BollingerBandsStrategyCombinator,
)
from algo_royale.backtester.strategy_factory.signal.strategy_factory import (
    StrategyFactory,
)
from algo_royale.backtester.walkforward.walk_forward_coordinator import (
    WalkForwardCoordinator,
)
from algo_royale.backtester.watchlist.watchlist import load_watchlist, save_watchlist
from algo_royale.clients.alpaca.alpaca_client_config import TradingConfig
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import (
    AlpacaCorporateActionClient,
)
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import (
    AlpacaNewsClient,
)
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import (
    AlpacaScreenerClient,
)
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stock_client import (
    AlpacaStockClient,
)
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stream_client import (
    AlpacaStreamClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_accounts_client import (
    AlpacaAccountClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_assets_client import (
    AlpacaAssetsClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_calendar_client import (
    AlpacaCalendarClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_clock_client import (
    AlpacaClockClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import (
    AlpacaOrdersClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_portfolio_client import (
    AlpacaPortfolioClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_positions_client import (
    AlpacaPositionsClient,
)
from algo_royale.clients.alpaca.alpaca_trading.alpaca_watchlist_client import (
    AlpacaWatchlistClient,
)
from algo_royale.clients.db.dao.indicator_dao import IndicatorDAO
from algo_royale.clients.db.dao.news_sentiment_dao import NewsSentimentDAO
from algo_royale.clients.db.dao.stock_data_dao import StockDataDAO
from algo_royale.clients.db.dao.trade_dao import TradeDAO
from algo_royale.clients.db.dao.trade_signal_dao import TradeSignalDAO
from algo_royale.clients.db.database import Database
from algo_royale.config.config import Config
from algo_royale.logging.loggable import TaggableLogger
from algo_royale.logging.logger_env import LoggerEnv
from algo_royale.logging.logger_factory import (
    LoggerFactory,
    LoggerType,
)
from algo_royale.services.db.indicator_service import IndicatorService
from algo_royale.services.db.news_sentiment_service import NewsSentimentService
from algo_royale.services.db.stock_data_service import StockDataService
from algo_royale.services.db.trade_service import TradeService
from algo_royale.services.db.trade_signal_service import TradeSignalService
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService
from algo_royale.utils.path_utils import get_data_dir
from algo_royale.visualization.dashboard import BacktestDashboard


class DIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    # Load configuration
    config = providers.Singleton(Config, config_file="config.ini")
    secrets = providers.Singleton(Config, config_file="secrets.ini")
    dao_sql_dir = providers.Callable(
        lambda config: config.get("paths.db", "sql_dir"), config=config
    )

    trading_config = providers.Singleton(
        TradingConfig,
        config=config,
        secrets=secrets,
    )

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
    database = providers.Singleton(
        Database, logger=logger_trading, config=config, secrets=secrets
    )

    db_connection = providers.Callable(lambda db: db.connection_context(), db=database)

    indicator_dao = providers.Singleton(
        IndicatorDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading,
    )

    news_sentiment_dao = providers.Singleton(
        NewsSentimentDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading,
    )

    stock_data_dao = providers.Singleton(
        StockDataDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading,
    )

    trade_dao = providers.Singleton(
        TradeDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading,
    )

    trade_signal_dao = providers.Singleton(
        TradeSignalDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading,
    )

    indicator_service = providers.Singleton(IndicatorService, dao=indicator_dao)

    news_sentiment_service = providers.Singleton(
        NewsSentimentService, dao=news_sentiment_dao
    )

    stock_data_Service = providers.Singleton(StockDataService, dao=stock_data_dao)

    trade_service = providers.Singleton(TradeService, dao=trade_dao)

    trade_signal_service = providers.Singleton(TradeSignalService, dao=trade_signal_dao)

    alpaca_corporate_action_client = providers.Factory(
        AlpacaCorporateActionClient, trading_config=trading_config
    )

    alpaca_news_client = providers.Factory(
        AlpacaNewsClient, trading_config=trading_config
    )

    alpaca_screener_client = providers.Factory(
        AlpacaScreenerClient, trading_config=trading_config
    )

    alpaca_stock_client = providers.Factory(
        AlpacaStockClient, trading_config=trading_config
    )

    alpaca_stream_client = providers.Factory(
        AlpacaStreamClient, trading_config=trading_config
    )

    alpaca_account_client = providers.Factory(
        AlpacaAccountClient, trading_config=trading_config
    )

    alpaca_assets_client = providers.Factory(
        AlpacaAssetsClient, trading_config=trading_config
    )

    alpaca_calendar_client = providers.Factory(
        AlpacaCalendarClient, trading_config=trading_config
    )

    alpaca_clock_client = providers.Factory(
        AlpacaClockClient, trading_config=trading_config
    )

    alpaca_orders_client = providers.Factory(
        AlpacaOrdersClient, trading_config=trading_config
    )

    alpaca_portfolio_client = providers.Factory(
        AlpacaPortfolioClient, trading_config=trading_config
    )

    alpaca_positions_client = providers.Factory(
        AlpacaPositionsClient, trading_config=trading_config
    )

    alpaca_watchlist_client = providers.Factory(
        AlpacaWatchlistClient, trading_config=trading_config
    )

    alpaca_quote_service = providers.Singleton(
        AlpacaQuoteService, alpaca_stock_client=alpaca_stock_client
    )

    data_dir = get_data_dir()
    ## Backtester
    stage_data_manager = providers.Singleton(
        StageDataManager, data_dir=data_dir, logger=logger_stage_data_manager
    )

    stage_data_preparer = providers.Singleton(
        StageDataPreparer,
        stage_data_manager=stage_data_manager,
        logger=logger_stage_data_preparer,
    )

    watchlist_path_string = providers.Object(
        config().get("backtester.paths", "watchlist_path")
    )
    load_watchlist_func = providers.Object(load_watchlist)
    save_watchlist_func = providers.Object(save_watchlist)

    stage_data_loader = providers.Singleton(
        StageDataLoader,
        logger=logger_stage_data_loader,
        stage_data_manager=stage_data_manager,
        load_watchlist=load_watchlist_func,
        watchlist_path_string=watchlist_path_string,
    )

    stage_data_writer = providers.Singleton(
        StageDataWriter,
        logger=logger_stage_data_writer,
        stage_data_manager=stage_data_manager,
    )

    feature_engineering_func = providers.Object(
        partial(feature_engineering, logger=logger_backtest_feature_engineering())
    )

    feature_engineer = providers.Singleton(
        FeatureEngineer,
        feature_engineering_func=feature_engineering_func,
        logger=logger_backtest_feature_engineering,
    )

    backtest_dashboard = providers.Singleton(
        BacktestDashboard,
        config=config,
    )

    symbol_strategy_data_loader = providers.Singleton(
        SymbolStrategyDataLoader,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        logger=logger_symbol_strategy_data_loader,
    )

    symbol_strategy_data_writer = providers.Singleton(
        SymbolStrategyDataWriter,
        stage_data_manager=stage_data_manager,
        data_writer=stage_data_writer,
        logger=logger_symbol_strategy_data_writer,
    )

    data_ingest_stage_coordinator = providers.Singleton(
        DataIngestStageCoordinator,
        data_loader=stage_data_loader,
        data_writer=symbol_strategy_data_writer,
        logger=logger_backtest_data_ingest,
        quote_service=alpaca_quote_service,
        load_watchlist=load_watchlist_func,
        watchlist_path_string=watchlist_path_string,
    )

    feature_engineering_stage_coordinator = providers.Singleton(
        FeatureEngineeringStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        data_writer=symbol_strategy_data_writer,
        stage_data_manager=stage_data_manager,
        logger=logger_backtest_feature_engineering,
        feature_engineer=feature_engineer,
    )

    # Strategy backtest executor
    strategy_executor = providers.Singleton(
        StrategyBacktestExecutor,
        stage_data_manager=stage_data_manager,
        logger=logger_strategy_executor,
    )
    strategy_evaluator = providers.Singleton(
        SignalBacktestEvaluator,
        logger=logger_strategy_evaluator,
    )

    signal_strategy_combinators = [
        BollingerBandsStrategyCombinator,
        # ComboStrategyCombinator,
        # MACDTrailingStrategyCombinator,
        # MeanReversionStrategyCombinator,
        # MomentumStrategyCombinator,
        # MovingAverageCrossoverStrategyCombinator,
        # MovingAverageStrategyCombinator,
        # PullbackEntryStrategyCombinator,
        # RSIStrategyCombinator,
        # TimeOfDayBiasStrategyCombinator,
        # TrailingStopStrategyCombinator,
        # TrendScraperStrategyCombinator,
        # VolatilityBreakoutStrategyCombinator,
        # VolumeSurgeStrategyCombinator,
        # VWAPReversionStrategyCombinator,
        # WickReversalStrategyCombinator,
    ]

    strategy_factory = providers.Singleton(
        StrategyFactory,
        strategy_map_path=providers.Object(
            config().get("backtester.signal.paths", "signal_strategy_map_path")
        ),
        strategy_combinators=signal_strategy_combinators,
        logger=logger_strategy_factory,
    )

    signal_strategy_optimizer_factory = providers.Singleton(
        SignalStrategyOptimizerFactoryImpl,
        logger=logger_signal_strategy_optimizer,
    )

    strategy_optimization_stage_coordinator = providers.Singleton(
        StrategyOptimizationStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        logger=logger_backtest_signal_optimization,
        strategy_combinators=signal_strategy_combinators,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_optimization_json_filename"
            )
        ),
        signal_strategy_optimizer_factory=signal_strategy_optimizer_factory,
    )

    strategy_testing_stage_coordinator = providers.Singleton(
        StrategyTestingStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
        strategy_factory=strategy_factory,
        logger=logger_backtest_signal_testing,
        strategy_combinators=signal_strategy_combinators,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_optimization_json_filename"
            )
        ),
    )

    strategy_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        data_ingest_stage_coordinator=data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=feature_engineering_stage_coordinator,
        optimization_stage_coordinator=strategy_optimization_stage_coordinator,
        testing_stage_coordinator=strategy_testing_stage_coordinator,
        logger=logger_strategy_walk_forward,
    )

    portfolio_executor = providers.Singleton(
        PortfolioBacktestExecutor,
        initial_balance=providers.Object(
            config().get_float(
                "backtester.portfolio", "initial_portfolio_value", 1_000_000.0
            )
        ),
        transaction_cost=providers.Object(
            config().get_float("backtester.portfolio", "transaction_costs", 0.0)
        ),
        min_lot=providers.Object(
            config().get_int("backtester.portfolio", "minimum_lot_size", 1)
        ),
        leverage=providers.Object(
            config().get_float("backtester.portfolio", "leverage", 1.0)
        ),
        slippage=providers.Object(
            config().get_float("backtester.portfolio", "slippage", 0.0)
        ),
        logger=logger_portfolio_executor,
    )

    portfolio_evaluator = providers.Singleton(
        PortfolioBacktestEvaluator,
        logger=logger_portfolio_evaluator,
    )

    portfolio_strategy_combinators = [
        EqualRiskContributionPortfolioStrategyCombinator,
        # EqualWeightPortfolioStrategyCombinator,
        # InverseVolatilityPortfolioStrategyCombinator,
        # MaxSharpePortfolioStrategyCombinator,
        # MeanVariancePortfolioStrategyCombinator,
        # MinimumVariancePortfolioStrategyCombinator,
        # MomentumPortfolioStrategyCombinator,
        # RiskParityPortfolioStrategyCombinator,
        # VolatilityWeightedPortfolioStrategyCombinator,
        # WinnerTakesAllPortfolioStrategyCombinator,
    ]

    portfolio_asset_matrix_preparer = providers.Singleton(
        AssetMatrixPreparer,
        logger=logger_portfolio_asset_matrix_preparer,
    )

    portfolio_strategy_optimizer_factory = providers.Singleton(
        PortfolioStrategyOptimizerFactoryImpl,
        logger=logger_portfolio_strategy_optimizer,
    )

    portfolio_optimization_stage_coordinator = providers.Singleton(
        PortfolioOptimizationStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        executor=portfolio_executor,
        evaluator=portfolio_evaluator,
        logger=logger_backtest_portfolio_optimization,
        strategy_combinators=portfolio_strategy_combinators,
        optimization_root=providers.Object(
            config().get(
                "backtester.portfolio.paths", "portfolio_optimization_root_path"
            )
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames", "portfolio_optimization_json_filename"
            )
        ),
        asset_matrix_preparer=portfolio_asset_matrix_preparer,
        portfolio_strategy_optimizer_factory=portfolio_strategy_optimizer_factory,
    )

    portfolio_testing_stage_coordinator = providers.Singleton(
        PortfolioTestingStageCoordinator,
        data_loader=symbol_strategy_data_loader,
        stage_data_manager=stage_data_manager,
        executor=portfolio_executor,
        evaluator=portfolio_evaluator,
        logger=logger_backtest_portfolio_testing,
        strategy_combinators=portfolio_strategy_combinators,
        optimization_root=providers.Object(
            config().get(
                "backtester.portfolio.paths", "portfolio_optimization_root_path"
            ),
        ),
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames", "portfolio_optimization_json_filename"
            )
        ),
        asset_matrix_preparer=portfolio_asset_matrix_preparer,
    )

    portfolio_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        stage_data_manager=stage_data_manager,
        stage_data_loader=stage_data_loader,
        data_ingest_stage_coordinator=data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=feature_engineering_stage_coordinator,
        optimization_stage_coordinator=portfolio_optimization_stage_coordinator,
        testing_stage_coordinator=portfolio_testing_stage_coordinator,
        logger=logger_portfolio_walk_forward,
    )

    strategy_evaluation_coordinator = providers.Singleton(
        StrategyEvaluationCoordinator,
        logger=logger_strategy_evaluation,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        evaluation_type=StrategyEvaluationType.BOTH,
        optimization_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_optimization_json_filename"
            )
        ),
        evaluation_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_evaluation_json_filename"
            )
        ),
    )

    symbol_evaluation_coordinator = providers.Singleton(
        SymbolEvaluationCoordinator,
        optimization_root=providers.Object(
            config().get("backtester.signal.paths", "signal_optimization_root_path")
        ),
        evaluation_json_filename=providers.Object(
            config().get(
                "backtester.signal.filenames", "signal_evaluation_json_filename"
            )
        ),
        summary_json_filename=providers.Object(
            config().get("backtester.signal.filenames", "signal_summary_json_filename")
        ),
        viability_threshold=providers.Object(
            config().get_float(
                "backtester.signal", "signal_evaluation_viability_threshold", 0.5
            )
        ),
        logger=logger_symbol_evaluation,
    )

    portfolio_evaluation_coordinator = providers.Singleton(
        PortfolioEvaluationCoordinator,
        logger=logger_portfolio_evaluation,
        optimization_root=providers.Object(
            config().get(
                "backtester.portfolio.paths", "portfolio_optimization_root_path"
            )
        ),
        strategy_window_evaluation_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames",
                "portfolio_evaluation_json_filename",
            )
        ),
        strategy_summary_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames", "portfolio_summary_json_filename"
            )
        ),
        global_summary_json_filename=providers.Object(
            config().get(
                "backtester.portfolio.filenames",
                "portfolio_global_summary_json_filename",
            )
        ),
        viability_threshold=providers.Object(
            config().get_float(
                "backtester.portfolio", "strategy_viability_threshold", 0.5
            )
        ),
    )
    pipeline_coordinator = providers.Singleton(
        PipelineCoordinator,
        strategy_walk_forward_coordinator=strategy_walk_forward_coordinator,
        portfolio_walk_forward_coordinator=portfolio_walk_forward_coordinator,
        strategy_evaluation_coordinator=strategy_evaluation_coordinator,
        symbol_evaluation_coordinator=symbol_evaluation_coordinator,
        portfolio_evaluation_coordinator=portfolio_evaluation_coordinator,
        logger=logger_backtest_pipeline,
    )


di_container = DIContainer()
