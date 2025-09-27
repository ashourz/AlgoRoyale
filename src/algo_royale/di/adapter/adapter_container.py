from algo_royale.adapters.account_cash_adapter import AccountCashAdapter
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

# Refactored AdapterContainer to assign sub-containers and adapters as attributes in __init__


class AdapterContainer:
    """Adapter Container"""

    def __init__(self, config, secrets, logger_container: LoggerContainer):
        self.config = config
        self.secrets = secrets
        self.logger_container = logger_container

    # Initialize client_container as an attribute
    @property
    def client_container(self) -> ClientContainer:
        return ClientContainer(
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )

    # MARKET DATA ADAPTERS
    @property
    def corporate_action_adapter(self) -> CorporateActionAdapter:
        return CorporateActionAdapter(
            client=self.client_container.alpaca_corporate_action_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.CORPORATE_ACTION_ADAPTER
            ),
        )

    @property
    def news_adapter(self) -> NewsAdapter:
        return NewsAdapter(
            client=self.client_container.alpaca_news_client,
            logger=self.logger_container.logger(logger_type=LoggerType.NEWS_ADAPTER),
        )

    @property
    def quote_adapter(self) -> QuoteAdapter:
        return QuoteAdapter(
            client=self.client_container.alpaca_quote_client,
            logger=self.logger_container.logger(logger_type=LoggerType.QUOTE_ADAPTER),
        )

    @property
    def screener_adapter(self) -> ScreenerAdapter:
        return ScreenerAdapter(
            client=self.client_container.alpaca_screener_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SCREENER_ADAPTER
            ),
        )

    @property
    def stream_adapter(self) -> StreamAdapter:
        return StreamAdapter(
            stream_client=self.client_container.alpaca_stream_client,
            logger=self.logger_container.logger(logger_type=LoggerType.STREAM_ADAPTER),
        )

    # TRADE ADAPTERS
    @property
    def account_adapter(self) -> AccountAdapter:
        return AccountAdapter(
            client=self.client_container.alpaca_account_client,
            logger=self.logger_container.logger(logger_type=LoggerType.ACCOUNT_ADAPTER),
        )

    # AccountCashAdapter wiring
    @property
    def account_cash_adapter(self) -> AccountCashAdapter:
        return AccountCashAdapter(
            account_adapter=self.account_adapter,
            logger=self.logger_container.logger(logger_type=LoggerType.ACCOUNT_ADAPTER),
        )

    @property
    def assets_adapter(self) -> AssetsAdapter:
        return AssetsAdapter(
            assets_client=self.client_container.alpaca_assets_client,
            logger=self.logger_container.logger(logger_type=LoggerType.ASSETS_ADAPTER),
        )

    @property
    def calendar_adapter(self) -> CalendarAdapter:
        return CalendarAdapter(
            calendar_client=self.client_container.alpaca_calendar_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.CALENDAR_ADAPTER
            ),
        )

    @property
    def clock_adapter(self) -> ClockAdapter:
        return ClockAdapter(
            clock_client=self.client_container.alpaca_clock_client,
            logger=self.logger_container.logger(logger_type=LoggerType.CLOCK_ADAPTER),
        )

    @property
    def order_stream_adapter(self) -> OrderStreamAdapter:
        return OrderStreamAdapter(
            order_stream_client=self.client_container.alpaca_order_stream_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ORDER_STREAM_ADAPTER
            ),
        )

    @property
    def orders_adapter(self) -> OrdersAdapter:
        return OrdersAdapter(
            client=self.client_container.alpaca_orders_client,
            logger=self.logger_container.logger(logger_type=LoggerType.ORDERS_ADAPTER),
        )

    @property
    def portfolio_adapter(self) -> PortfolioAdapter:
        return PortfolioAdapter(
            client=self.client_container.alpaca_portfolio_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_ADAPTER
            ),
        )

    @property
    def positions_adapter(self) -> PositionsAdapter:
        return PositionsAdapter(
            client=self.client_container.alpaca_positions_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.POSITIONS_ADAPTER
            ),
        )

    @property
    def watchlist_adapter(self) -> WatchlistAdapter:
        return WatchlistAdapter(
            client=self.client_container.alpaca_watchlist_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.WATCHLIST_ADAPTER
            ),
        )

    async def async_close(self):
        """Close resources like database connections."""
        await self.client_container.async_close_all_clients()
