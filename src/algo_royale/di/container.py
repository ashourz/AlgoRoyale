from functools import partial

from dependency_injector import containers, providers

from algo_royale.backtester.data_preparer.async_data_preparer import AsyncDataPreparer
from algo_royale.backtester.data_preparer.data_preparer import DataPreparer
from algo_royale.backtester.data_stream.normalized_data_stream_factory import (
    NormalizedDataStreamFactory,
)
from algo_royale.backtester.evaluator.backtest.simple_backtest_evaluator import (
    SimpleBacktestEvaluator,
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
from algo_royale.backtester.executor.strategy_backtest_executor import (
    StrategyBacktestExecutor,
)
from algo_royale.backtester.feature_engineering.feature_engineer import FeatureEngineer
from algo_royale.backtester.feature_engineering.feature_engineering import (
    feature_engineering,
)
from algo_royale.backtester.pipeline.pipeline_coordinator import PipelineCoordinator
from algo_royale.backtester.stage_coordinator.data_ingest_stage_coordinator import (
    DataIngestStageCoordinator,
)
from algo_royale.backtester.stage_coordinator.feature_engineering_stage_coordinator import (
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
from algo_royale.backtester.stage_data.stage_data_loader import StageDataLoader
from algo_royale.backtester.stage_data.stage_data_manager import StageDataManager
from algo_royale.backtester.stage_data.stage_data_writer import StageDataWriter
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
from algo_royale.logging.logger_singleton import (
    Environment,
    LoggerSingleton,
    LoggerType,
)
from algo_royale.services.db.indicator_service import IndicatorService
from algo_royale.services.db.news_sentiment_service import NewsSentimentService
from algo_royale.services.db.stock_data_service import StockDataService
from algo_royale.services.db.trade_service import TradeService
from algo_royale.services.db.trade_signal_service import TradeSignalService
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService
from algo_royale.strategy_factory.combinator.bollinger_bands_strategy_combinator import (
    BollingerBandsStrategyCombinator,
)
from algo_royale.strategy_factory.strategy_factory import StrategyFactory
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

    logger_backtest_prod = providers.Callable(
        LoggerSingleton.get_instance,
        logger_type=LoggerType.BACKTESTING,
        environment=Environment.PRODUCTION,
    )

    logger_trading_prod = providers.Callable(
        LoggerSingleton.get_instance,
        logger_type=LoggerType.TRADING,
        environment=Environment.PRODUCTION,
    )

    database = providers.Singleton(
        Database, logger=logger_trading_prod, config=config, secrets=secrets
    )

    db_connection = providers.Callable(lambda db: db.connection_context(), db=database)

    indicator_dao = providers.Singleton(
        IndicatorDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading_prod,
    )

    news_sentiment_dao = providers.Singleton(
        NewsSentimentDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading_prod,
    )

    stock_data_dao = providers.Singleton(
        StockDataDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading_prod,
    )

    trade_dao = providers.Singleton(
        TradeDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading_prod,
    )

    trade_signal_dao = providers.Singleton(
        TradeSignalDAO,
        connection=db_connection,
        sql_dir=dao_sql_dir,
        logger=logger_trading_prod,
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

    ## Backtester
    stage_data_manager = providers.Singleton(
        StageDataManager, logger=logger_backtest_prod
    )

    data_preparer = providers.Singleton(DataPreparer, logger=logger_backtest_prod)

    async_data_preparer = providers.Singleton(
        AsyncDataPreparer, logger=logger_backtest_prod
    )

    normalized_data_stream_factory = providers.Singleton(
        NormalizedDataStreamFactory,
        data_preparer=data_preparer,
        logger=logger_backtest_prod,
    )

    watchlist_path_string = providers.Object(
        config().get("paths.backtester", "watchlist_path")
    )
    load_watchlist_func = providers.Object(load_watchlist)
    save_watchlist_func = providers.Object(save_watchlist)

    stage_data_loader = providers.Singleton(
        StageDataLoader,
        logger=logger_backtest_prod,
        stage_data_manager=stage_data_manager,
        load_watchlist=load_watchlist_func,
        watchlist_path_string=watchlist_path_string,
    )

    stage_data_writer = providers.Singleton(
        StageDataWriter,
        logger=logger_backtest_prod,
        stage_data_manager=stage_data_manager,
    )

    feature_engineering_func = providers.Object(
        partial(feature_engineering, logger=logger_backtest_prod())
    )

    feature_engineer = providers.Singleton(
        FeatureEngineer,
        feature_engineering_func=feature_engineering_func,
        logger=logger_backtest_prod,
    )

    backtest_dashboard = providers.Singleton(
        BacktestDashboard,
        config=config,
    )

    data_ingest_stage_coordinator = providers.Singleton(
        DataIngestStageCoordinator,
        data_loader=stage_data_loader,
        data_preparer=async_data_preparer,
        data_writer=stage_data_writer,
        stage_data_manager=stage_data_manager,
        logger=logger_backtest_prod,
        quote_service=alpaca_quote_service,
        load_watchlist=load_watchlist_func,
        watchlist_path_string=watchlist_path_string,
    )

    feature_engineering_stage_coordinator = providers.Singleton(
        FeatureEngineeringStageCoordinator,
        data_loader=stage_data_loader,
        data_preparer=async_data_preparer,
        data_writer=stage_data_writer,
        stage_data_manager=stage_data_manager,
        logger=logger_backtest_prod,
        feature_engineer=feature_engineer,
    )

    # Strategy backtest executor
    strategy_executor = providers.Singleton(
        StrategyBacktestExecutor,
        stage_data_manager=stage_data_manager,
        logger=logger_backtest_prod,
    )
    strategy_evaluator = providers.Singleton(
        SimpleBacktestEvaluator,
        logger=logger_backtest_prod,
    )

    strategy_factory = providers.Singleton(
        StrategyFactory,
        config=config,
        logger=logger_backtest_prod,
    )

    strategy_combinators = [
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

    strategy_optimization_stage_coordinator = providers.Singleton(
        StrategyOptimizationStageCoordinator,
        data_loader=stage_data_loader,
        data_preparer=async_data_preparer,
        data_writer=stage_data_writer,
        stage_data_manager=stage_data_manager,
        strategy_factory=strategy_factory,
        logger=logger_backtest_prod,
        strategy_combinators=strategy_combinators,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
    )

    strategy_testing_stage_coordinator = providers.Singleton(
        StrategyTestingStageCoordinator,
        data_loader=stage_data_loader,
        data_preparer=async_data_preparer,
        data_writer=stage_data_writer,
        stage_data_manager=stage_data_manager,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
        strategy_factory=strategy_factory,
        logger=logger_backtest_prod,
        strategy_combinators=strategy_combinators,
    )

    strategy_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        data_ingest_stage_coordinator=data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=feature_engineering_stage_coordinator,
        optimization_stage_coordinator=strategy_optimization_stage_coordinator,
        testing_stage_coordinator=strategy_testing_stage_coordinator,
        logger=logger_backtest_prod,
    )

    portfolio_optimization_stage_coordinator = providers.Singleton(
        PortfolioOptimizationStageCoordinator,
        data_loader=stage_data_loader,
        data_preparer=async_data_preparer,
        data_writer=stage_data_writer,
        stage_data_manager=stage_data_manager,
        strategy_factory=strategy_factory,
        logger=logger_backtest_prod,
        strategy_combinators=strategy_combinators,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
    )

    portfolio_testing_stage_coordinator = providers.Singleton(
        PortfolioTestingStageCoordinator,
        data_loader=stage_data_loader,
        data_preparer=async_data_preparer,
        data_writer=stage_data_writer,
        stage_data_manager=stage_data_manager,
        strategy_executor=strategy_executor,
        strategy_evaluator=strategy_evaluator,
        strategy_factory=strategy_factory,
        logger=logger_backtest_prod,
        strategy_combinators=strategy_combinators,
    )

    portfolio_walk_forward_coordinator = providers.Singleton(
        WalkForwardCoordinator,
        data_ingest_stage_coordinator=data_ingest_stage_coordinator,
        feature_engineering_stage_coordinator=feature_engineering_stage_coordinator,
        optimization_stage_coordinator=strategy_optimization_stage_coordinator,
        testing_stage_coordinator=strategy_testing_stage_coordinator,
        logger=logger_backtest_prod,
    )

    strategy_evaluation_coordinator = providers.Singleton(
        StrategyEvaluationCoordinator,
        logger=logger_backtest_prod,
        optimization_root_path=providers.Object(
            config().get("paths.backtester", "optimization_root_path")
        ),
        evaluation_type=StrategyEvaluationType.BOTH,
        optimization_json_filename=providers.Object(
            config().get("paths.backtester", "optimization_json_filename")
        ),
        evaluation_json_filename=providers.Object(
            config().get("paths.backtester", "evaluation_json_filename")
        ),
    )

    symbol_evaluation_coordinator = providers.Singleton(
        SymbolEvaluationCoordinator,
        optimization_root=providers.Object(
            config().get("paths.backtester", "optimization_root_path")
        ),
        evaluation_json_filename=providers.Object(
            config().get("paths.backtester", "evaluation_json_filename")
        ),
        summary_json_filename=providers.Object(
            config().get("paths.backtester", "summary_json_filename")
        ),
        viability_threshold=0.75,
    )

    pipeline_coordinator = providers.Singleton(
        PipelineCoordinator,
        walk_forward_coordinator=strategy_walk_forward_coordinator,
        strategy_evaluation_coordinator=strategy_evaluation_coordinator,
        symbol_evaluation_coordinator=symbol_evaluation_coordinator,
        logger=logger_backtest_prod,
    )


di_container = DIContainer()
