from dependency_injector import containers, providers

from algo_royale.adapters.market_data.corporate_action_adapter import (
    CorporateActionAdapter,
)
from algo_royale.adapters.market_data.news_adapter import NewsAdapter
from algo_royale.adapters.market_data.quote_adapter import QuoteAdapter
from algo_royale.adapters.market_data.screener_adapter import ScreenerAdapter
from algo_royale.adapters.market_data.stream_adapter import StreamAdapter
from algo_royale.adapters.trading.account_adapter import AccountAdapter
from algo_royale.adapters.trading.assets_adapter import AssetsAdapter
from algo_royale.adapters.trading.calendar_adapter import CalendarAdapter
from algo_royale.adapters.trading.clock_adapter import ClockAdapter
from algo_royale.adapters.trading.order_stream_adapter import OrderStreamAdapter
from algo_royale.adapters.trading.orders_adapter import OrdersAdapter
from algo_royale.adapters.trading.portfolio_adapter import PortfolioAdapter
from algo_royale.adapters.trading.positions_adapter import PositionsAdapter
from algo_royale.adapters.trading.watchlist_adapter import WatchlistAdapter
from algo_royale.di.adapter.client_container import ClientContainer
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class AdapterContainer(containers.DeclarativeContainer):
    """Adapter Container"""

    config = providers.Configuration()
    secrets = providers.Configuration()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    client_container = providers.Container(
        ClientContainer,
        config=config,
        secrets=secrets,
        logger_container=logger_container,
    )

    ## MARKET DATA ADAPTERS
    corporate_action_adapter = providers.Singleton(
        CorporateActionAdapter,
        client=client_container.alpaca_corporate_action_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.CORPORATE_ACTION_ADAPTER
            ),
            logger_container,
        ),
    )

    news_adapter = providers.Singleton(
        NewsAdapter,
        client=client_container.alpaca_news_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.NEWS_ADAPTER
            ),
            logger_container,
        ),
    )

    quote_adapter = providers.Singleton(
        QuoteAdapter,
        client=client_container.alpaca_stock_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.QUOTE_ADAPTER
            ),
            logger_container,
        ),
    )

    screener_adapter = providers.Singleton(
        ScreenerAdapter,
        client=client_container.alpaca_screener_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.SCREENER_ADAPTER
            ),
            logger_container,
        ),
    )

    stream_adapter = providers.Singleton(
        StreamAdapter,
        stream_client=client_container.alpaca_stream_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.STREAM_ADAPTER
            ),
            logger_container,
        ),
    )

    ## TRADE ADAPTERS
    account_adapter = providers.Singleton(
        AccountAdapter,
        client=client_container.alpaca_account_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ACCOUNT_ADAPTER
            ),
            logger_container,
        ),
    )

    assets_adapter = providers.Singleton(
        AssetsAdapter,
        client=client_container.alpaca_assets_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ASSETS_ADAPTER
            ),
            logger_container,
        ),
    )

    calendar_adapter = providers.Singleton(
        CalendarAdapter,
        client=client_container.alpaca_calendar_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.CALENDAR_ADAPTER
            ),
            logger_container,
        ),
    )

    clock_adapter = providers.Singleton(
        ClockAdapter,
        client=client_container.alpaca_clock_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.CLOCK_ADAPTER
            ),
            logger_container,
        ),
    )

    order_stream_adapter = providers.Singleton(
        OrderStreamAdapter,
        order_stream_client=client_container.alpaca_order_stream_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ORDER_STREAM_ADAPTER
            ),
            logger_container,
        ),
    )

    orders_adapter = providers.Singleton(
        OrdersAdapter,
        client=client_container.alpaca_orders_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ORDERS_ADAPTER
            ),
            logger_container,
        ),
    )

    portfolio_adapter = providers.Singleton(
        PortfolioAdapter,
        client=client_container.alpaca_portfolio_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_ADAPTER
            ),
            logger_container,
        ),
    )

    positions_adapter = providers.Singleton(
        PositionsAdapter,
        client=client_container.alpaca_positions_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.POSITIONS_ADAPTER
            ),
            logger_container,
        ),
    )

    watchlist_adapter = providers.Singleton(
        WatchlistAdapter,
        client=client_container.alpaca_watchlist_client,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.WATCHLIST_ADAPTER
            ),
            logger_container,
        ),
    )
