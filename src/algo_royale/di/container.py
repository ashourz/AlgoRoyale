from dependency_injector import containers, providers

from algo_royale.config.config import Config
from algo_royale.clients.db import DatabaseClient
from algo_royale.clients.alpaca.alpaca_base_client import AlpacaBaseClient
from algo_royale.clients.alpaca.alpaca_market_data.alpaca_stock_client import AlpacaStockClient
from algo_royale.services.trading.alpaca_orders_service import AlpacaOrdersService
from algo_royale.services.db.trade_service import TradeService


class DIContainer(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    # Load configuration
    config = providers.Singleton(Config, config_file="config.ini")
    secrets = providers.Singleton(Config, config_file="secrets.ini")

    # Database Client
    # db_client = providers.Singleton(
    #     DatabaseClient,
    #     db_config=config().get_section("database"),
    # )

    # # Alpaca Base Client
    # alpaca_base_client = providers.Singleton(
    #     AlpacaBaseClient,
    #     api_key=config().get_section("alpaca")["api_key_header"],
    #     api_secret=config().get_section("alpaca")["api_secret_header"],
    #     base_url=config().get_section("alpaca")["base_url_trading_paper"],
    # )

    # # Alpaca Stock Client
    # alpaca_stock_client = providers.Singleton(
    #     AlpacaStockClient,
    #     base_client=alpaca_base_client,
    # )

    # # Alpaca Order Service
    # alpaca_orders_service = providers.Factory(
    #     AlpacaOrdersService,
    #     alpaca_client=alpaca_base_client,
    # )

    # # Trade Service
    # trade_service = providers.Factory(
    #     TradeService,
    #     db_client=db_client,
    # )
    
di = DIContainer()