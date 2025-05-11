from algo_royale.backtester.core.engine import BacktestEngine
from algo_royale.backtester.main import BacktestRunner
from algo_royale.backtester.utils.data_loader import BacktestDataLoader
from algo_royale.backtester.utils.results_saver import BacktestResultsSaver
from algo_royale.clients.alpaca.alpaca_client_config import TradingConfig
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stream_client import AlpacaStreamClient
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_screener_client import AlpacaScreenerClient
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_corporate_action_client import AlpacaCorporateActionClient
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_news_client import AlpacaNewsClient
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stock_client import AlpacaStockClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_positions_client import AlpacaPositionsClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_accounts_client import AlpacaAccountClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_assets_client import AlpacaAssetsClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_calendar_client import AlpacaCalendarClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_clock_client import AlpacaClockClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_orders_client import AlpacaOrdersClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_portfolio_client import AlpacaPortfolioClient
from algo_royale.clients.alpaca.alpaca_trading.alpaca_watchlist_client import AlpacaWatchlistClient
from algo_royale.logging.logger_singleton import Environment, LoggerSingleton, LoggerType
from algo_royale.services.market_data.alpaca_stock_service import AlpacaQuoteService
from algo_royale.visualization.dashboard import BacktestDashboard
from dependency_injector import containers, providers
from algo_royale.config.config import Config

class DIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    # Load configuration
    config = providers.Singleton(Config, config_file="config.ini")
    secrets = providers.Singleton(Config, config_file="secrets.ini")

    trading_config = providers.Singleton(
        TradingConfig,
        config=config,
        secrets=secrets,
    )
    
    logger_backtest_prod = providers.Singleton(
        LoggerSingleton,
        logger_type=LoggerType.BACKTESTING,
        environment=Environment.PRODUCTION
    )
    
    alpaca_corporate_action_client = providers.Factory(
        AlpacaCorporateActionClient,
        trading_config=trading_config
    )
    
    alpaca_news_client = providers.Factory(
        AlpacaNewsClient,
        trading_config=trading_config
    )
    
    alpaca_screener_client = providers.Factory(
        AlpacaScreenerClient,
        trading_config=trading_config
    )
    
    alpaca_stock_client = providers.Factory(
        AlpacaStockClient,
        trading_config=trading_config
    )

    alpaca_stream_client = providers.Factory(
        AlpacaStreamClient,
        trading_config=trading_config
    )

    alpaca_account_client = providers.Factory(
        AlpacaAccountClient,
        trading_config=trading_config
    )
    
    alpaca_assets_client = providers.Factory(
        AlpacaAssetsClient,
        trading_config=trading_config
    )
    
    alpaca_calendar_client = providers.Factory( 
        AlpacaCalendarClient,
        trading_config=trading_config
    )
    
    alpaca_clock_client = providers.Factory(
        AlpacaClockClient,
        trading_config=trading_config
    )
    
    alpaca_orders_client = providers.Factory(
        AlpacaOrdersClient,
        trading_config=trading_config
    )
    
    alpaca_portfolio_client = providers.Factory(
        AlpacaPortfolioClient,
        trading_config=trading_config
    )   
    
    alpaca_positions_client = providers.Factory(
        AlpacaPositionsClient,
        trading_config=trading_config
    )
    
    alpaca_watchlist_client = providers.Factory(
        AlpacaWatchlistClient,
        trading_config=trading_config
    )

    alpaca_quote_service = providers.Singleton(
        AlpacaQuoteService,
        alpaca_stock_client = alpaca_stock_client
    )
    
    #Backtest Data Loader
    backtest_data_loader = providers.Singleton(
        BacktestDataLoader,
        config=config,
        logger=logger_backtest_prod,
        quote_service = alpaca_quote_service
    )
    
    backtest_results_saver = providers.Singleton(
        BacktestResultsSaver,
        config=config,
        logger=logger_backtest_prod,
    )
    
    backtest_engine = providers.Singleton(
        BacktestEngine,
        results_saver=backtest_results_saver,
        logger= logger_backtest_prod
    )
     
    backtest_runner = providers.Singleton(
        BacktestRunner,
        data_loader=backtest_data_loader,
        engine = backtest_engine,
        logger= logger_backtest_prod
    )
    
   
    backtest_dashboard = providers.Singleton(
        BacktestDashboard,
        config=config,
    )
    
    
di_container = DIContainer()