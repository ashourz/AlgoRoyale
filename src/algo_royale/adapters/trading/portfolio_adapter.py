# src/algo_royale/services/alpaca_trading/alpaca_portfolio_service.py

from datetime import datetime
from typing import Optional

from algo_royale.clients.alpaca.alpaca_trading.alpaca_portfolio_client import (
    AlpacaPortfolioClient,
)
from algo_royale.clients.alpaca.exceptions import ParameterConflictError
from algo_royale.logging.loggable import Loggable
from algo_royale.models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
from algo_royale.models.alpaca_trading.enums.enums import IntradayReporting, PNLReset


class PortfolioAdapter:
    """Service class to manage portfolio data and history for Alpaca API."""

    def __init__(self, client: AlpacaPortfolioClient, logger: Loggable):
        self.client = client
        self.logger = logger

    async def get_portfolio_history(
        self,
        period: Optional[str] = None,
        timeframe: Optional[str] = None,
        intraday_reporting: Optional[IntradayReporting] = None,
        start: Optional[datetime] = None,
        pnl_reset: Optional[PNLReset] = None,
        end: Optional[datetime] = None,
        cashflow_types: Optional[str] = None,
    ) -> Optional[PortfolioPerformance]:
        """
        Fetches portfolio history from Alpaca API.

        Arguments are similar to AlpacaPortfolioClient's fetch_portfolio_history method,
        but this method serves as a wrapper for handling the client call.
        """

        # Validate parameters to ensure no conflicting arguments
        if period and start and end:
            raise ParameterConflictError(
                "Only two of start, end (or date_end) and period can be specified at the same time."
            )

        # Delegate the actual API request to AlpacaPortfolioClient
        return await self.client.fetch_portfolio_history(
            period=period,
            timeframe=timeframe,
            intraday_reporting=intraday_reporting,
            start=start,
            pnl_reset=pnl_reset,
            end=end,
            cashflow_types=cashflow_types,
        )
