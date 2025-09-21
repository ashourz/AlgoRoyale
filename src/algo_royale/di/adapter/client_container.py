from dependency_injector import containers, providers

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
from algo_royale.clients.alpaca.alpaca_trading.alpaca_order_stream_client import (
    AlpacaOrderStreamClient,
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
from algo_royale.di.logger_container import LoggerContainer
from algo_royale.logging.logger_type import LoggerType


class ClientContainer(containers.DeclarativeContainer):
    """Dependency injection container for clients."""

    config = providers.Configuration()
    secrets = providers.Configuration()
    logger_container: LoggerContainer = providers.DependenciesContainer()

    alpaca_corporate_action_client = providers.Factory(
        AlpacaCorporateActionClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_CORPORATE_ACTION_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.data.v1(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_news_client = providers.Factory(
        AlpacaNewsClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_NEWS_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.data.v1beta1(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_screener_client = providers.Factory(
        AlpacaScreenerClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_SCREENER_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.data.v1beta1(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_stock_client = providers.Factory(
        AlpacaStockClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_STOCK_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.data.v2(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_stream_client = providers.Factory(
        AlpacaStreamClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_STREAM_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.data.stream.v2(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_account_client = providers.Factory(
        AlpacaAccountClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_ACCOUNT_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_assets_client = providers.Factory(
        AlpacaAssetsClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_ASSETS_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_calendar_client = providers.Factory(
        AlpacaCalendarClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_CALENDAR_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_clock_client = providers.Factory(
        AlpacaClockClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_CLOCK_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_orders_client = providers.Factory(
        AlpacaOrdersClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_ORDERS_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_portfolio_client = providers.Factory(
        AlpacaPortfolioClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_PORTFOLIO_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_positions_client = providers.Factory(
        AlpacaPositionsClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_POSITIONS_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_watchlist_client = providers.Factory(
        AlpacaWatchlistClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_WATCHLIST_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )

    alpaca_order_stream_client = providers.Factory(
        AlpacaOrderStreamClient,
        logger=providers.Callable(
            lambda logger_container: logger_container.logger(
                logger_type=LoggerType.ALPACA_ORDER_STREAM_CLIENT
            ),
            logger_container,
        ),
        base_url=config.alpaca.urls.trading.stream(),
        api_key=secrets.alpaca.api_key(),
        api_secret=secrets.alpaca.api_secret(),
        api_key_header=config.alpaca.headers.api_key(),
        api_secret_header=config.alpaca.headers.api_secret(),
        http_timeout=config.alpaca.params.get("http_timeout", 10),
        reconnect_delay=config.alpaca.params.get("reconnect_delay", 5),
        keep_alive_timeout=config.alpaca.params.get("keep_alive_timeout", 20),
    )
