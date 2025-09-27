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


# Refactored ClientContainer to assign all clients as attributes in __init__
class ClientContainer:
    """Dependency injection container for clients."""

    def __init__(self, config, secrets, logger_container: LoggerContainer):
        self.config = config
        self.secrets = secrets
        self.logger_container = logger_container

    @property
    def alpaca_corporate_action_client(self) -> AlpacaCorporateActionClient:
        return AlpacaCorporateActionClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_CORPORATE_ACTION_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["data_v1"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_news_client(self) -> AlpacaNewsClient:
        return AlpacaNewsClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_NEWS_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["data_v1_beta1"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_screener_client(self) -> AlpacaScreenerClient:
        return AlpacaScreenerClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_SCREENER_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["data_v1_beta1"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_stock_client(self) -> AlpacaStockClient:
        return AlpacaStockClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_STOCK_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["data_v2"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_stream_client(self) -> AlpacaStreamClient:
        return AlpacaStreamClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_STREAM_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["data_stream_v2"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_account_client(self) -> AlpacaAccountClient:
        return AlpacaAccountClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_ACCOUNT_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_assets_client(self) -> AlpacaAssetsClient:
        return AlpacaAssetsClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_ASSETS_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_calendar_client(self) -> AlpacaCalendarClient:
        return AlpacaCalendarClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_CALENDAR_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_clock_client(self) -> AlpacaClockClient:
        return AlpacaClockClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_CLOCK_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_orders_client(self) -> AlpacaOrdersClient:
        return AlpacaOrdersClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_ORDERS_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_portfolio_client(self) -> AlpacaPortfolioClient:
        return AlpacaPortfolioClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_PORTFOLIO_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_positions_client(self) -> AlpacaPositionsClient:
        return AlpacaPositionsClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_POSITIONS_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_watchlist_client(self) -> AlpacaWatchlistClient:
        return AlpacaWatchlistClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_WATCHLIST_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    @property
    def alpaca_order_stream_client(self) -> AlpacaOrderStreamClient:
        return AlpacaOrderStreamClient(
            logger=self.logger_container.logger(
                logger_type=LoggerType.ALPACA_ORDER_STREAM_CLIENT
            ),
            base_url=self.config["alpaca_urls"]["trading_stream"],
            api_key=self.secrets["alpaca"]["api_key"],
            api_secret=self.secrets["alpaca"]["api_secret"],
            api_key_header=self.config["alpaca_headers"]["api_key"],
            api_secret_header=self.config["alpaca_headers"]["api_secret"],
            http_timeout=int(self.config["alpaca_params"]["http_timeout"]),
            reconnect_delay=int(self.config["alpaca_params"]["reconnect_delay"]),
            keep_alive_timeout=int(self.config["alpaca_params"]["keep_alive_timeout"]),
        )

    def close_all_clients(self):
        """Close all clients that have a close or aclose method."""
        try:
            for client in [
                self.alpaca_corporate_action_client,
                self.alpaca_news_client,
                self.alpaca_screener_client,
                self.alpaca_stock_client,
                self.alpaca_stream_client,
                self.alpaca_account_client,
                self.alpaca_assets_client,
                self.alpaca_calendar_client,
                self.alpaca_clock_client,
                self.alpaca_orders_client,
                self.alpaca_portfolio_client,
                self.alpaca_positions_client,
                self.alpaca_watchlist_client,
                self.alpaca_order_stream_client,
            ]:
                if hasattr(client, "aclose"):
                    import asyncio

                    asyncio.run(client.aclose())
                elif hasattr(client, "close"):
                    client.close()
        except Exception as e:
            self.logger_container.logger(logger_type=LoggerType.CLIENT_CONTAINER).error(
                f"Error closing clients: {e}"
            )
