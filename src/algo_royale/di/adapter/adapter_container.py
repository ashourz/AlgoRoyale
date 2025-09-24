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

        # REPOS (from RepoContainer)
        from algo_royale.di.repo.repo_container import RepoContainer

        self.repo_container = RepoContainer(
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )
        self.enriched_data_repo = self.repo_container.enriched_data_repo

        # Initialize client_container as an attribute
        self.client_container = ClientContainer(
            config=self.config,
            secrets=self.secrets,
            logger_container=self.logger_container,
        )

        # MARKET DATA ADAPTERS
        self.corporate_action_adapter = CorporateActionAdapter(
            client=self.client_container.alpaca_corporate_action_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.CORPORATE_ACTION_ADAPTER
            ),
        )

        self.news_adapter = NewsAdapter(
            client=self.client_container.alpaca_news_client,
            logger=self.logger_container.logger(logger_type=LoggerType.NEWS_ADAPTER),
        )

        self.quote_adapter = QuoteAdapter(
            alpaca_stock_client=self.client_container.alpaca_stock_client,
            logger=self.logger_container.logger(logger_type=LoggerType.QUOTE_ADAPTER),
        )

        self.screener_adapter = ScreenerAdapter(
            client=self.client_container.alpaca_screener_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.SCREENER_ADAPTER
            ),
        )

        self.stream_adapter = StreamAdapter(
            stream_client=self.client_container.alpaca_stream_client,
            logger=self.logger_container.logger(logger_type=LoggerType.STREAM_ADAPTER),
        )

        # TRADE ADAPTERS

        self.account_adapter = AccountAdapter(
            client=self.client_container.alpaca_account_client,
            logger=self.logger_container.logger(logger_type=LoggerType.ACCOUNT_ADAPTER),
        )

        # AccountCashAdapter wiring
        from algo_royale.adapters.account_cash_adapter import AccountCashAdapter

        self.account_cash_adapter = AccountCashAdapter(
            account_adapter=self.account_adapter,
            logger=self.logger_container.logger(logger_type=LoggerType.ACCOUNT_ADAPTER),
        )

        self.assets_adapter = AssetsAdapter(
            assets_client=self.client_container.alpaca_assets_client,
            logger=self.logger_container.logger(logger_type=LoggerType.ASSETS_ADAPTER),
        )

        self.calendar_adapter = CalendarAdapter(
            calendar_client=self.client_container.alpaca_calendar_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.CALENDAR_ADAPTER
            ),
        )

        self.clock_adapter = ClockAdapter(
            clock_client=self.client_container.alpaca_clock_client,
            logger=self.logger_container.logger(logger_type=LoggerType.CLOCK_ADAPTER),
        )

        self.order_stream_adapter = OrderStreamAdapter(
            order_stream_client=self.client_container.alpaca_order_stream_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.ORDER_STREAM_ADAPTER
            ),
        )

        self.orders_adapter = OrdersAdapter(
            client=self.client_container.alpaca_orders_client,
            logger=self.logger_container.logger(logger_type=LoggerType.ORDERS_ADAPTER),
        )

        # Alias for compatibility with code expecting order_adapter
        self.order_adapter = self.orders_adapter

        # Alias for compatibility with code expecting order_adapter
        self.order_adapter = self.orders_adapter

        self.portfolio_adapter = PortfolioAdapter(
            client=self.client_container.alpaca_portfolio_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.PORTFOLIO_ADAPTER
            ),
        )

        self.positions_adapter = PositionsAdapter(
            client=self.client_container.alpaca_positions_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.POSITIONS_ADAPTER
            ),
        )

        self.watchlist_adapter = WatchlistAdapter(
            client=self.client_container.alpaca_watchlist_client,
            logger=self.logger_container.logger(
                logger_type=LoggerType.WATCHLIST_ADAPTER
            ),
        )

    def close(self):
        """Close resources like database connections."""
        self.client_container.close_all_clients()
