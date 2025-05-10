## client\alpaca_trading\alpaca_portfolio_client.py

from datetime import datetime
from typing import Optional
from algo_royale.live_trading.client.alpaca_base_client import AlpacaBaseClient
from algo_royale.live_trading.client.exceptions import ParameterConflictError
from algo_royale.shared.models.alpaca_trading.alpaca_portfolio import PortfolioPerformance
from algo_royale.shared.models.alpaca_trading.enums import IntradayReporting, PNLReset
from algo_royale.live_trading.config.config import ALPACA_TRADING_URL

class AlpacaPortfolioClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for portfolio data.""" 
    

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaPortfolioClient"    
    
    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_TRADING_URL
    
    async def fetch_portfolio_history(
            self,
            period: Optional[str] = None,
            timeframe: Optional[str] = None,
            intraday_reporting:  Optional[IntradayReporting] = None,
            start: Optional[datetime] = None,
            pnl_reset: Optional[PNLReset] = None,
            end: Optional[datetime] = None,
            cashflow_types: Optional[str] = None
        ) -> Optional[PortfolioPerformance]:
        """
        Gets the portfolio history statistics for an account.
        
        Parameters:
            - period (str) : The duration of the data in number + unit format, such as 1D, where unit can be D for day, W for week, M for month and A for year. Defaults to 1M.
                
                Only two of start, end (or date_end) and period can be specified at the same time.
                For intraday timeframes (<1D) only 30 days or less can be queried, 
                for 1D resolutions there is no such limit, data is available since the creation of the account.
                
            - timeframe (str) : The resolution of time window. 1Min, 5Min, 15Min, 1H, or 1D. If omitted, 1Min for less than 7 days period, 15Min for less than 30 days, or otherwise 1D.
                
                For queries with longer than 30 days of period, the system only accepts 1D as timeframe.
            
            - intraday_reporting (IntradayReporting) : For intraday resolutions (<1D) this specfies which timestamps to return data points for.
            
            - start (datetime) : The timestamp the data is returned starting from in RFC3339 format (including timezone specification).
            
                - For timeframes less than 1D, the actual start will be determined based on the value of the intraday_reporting query parameter:
                - For example if the intraday_reporting is extended_hours, and the timestamp specified is 2023-10-19T03:30:00-04:00, 
                    then the first data point returned will be 2023-10-19T04:00:00-04:00 due to the session opening at that time. 
                - start, end (or date_end) and period cannot be specified at the same time.
                - If unset, the period will be used to calculate the starting time.
                
            - pnl_reset (PNLReset) : pnl_reset defines how we are calculating the baseline values for Profit And Loss (pnl) for queries with timeframe less than 1D (intraday queries).
                - The default behavior for intraday queries is that we reset the pnl value to the previous day's closing equity for each trading day.
                - In case of crypto (given it's continous nature), this might not be desired: 
                    specifying "no_reset" disables this behavior and all pnl values returned will be relative to the closing equity of the previous trading day.
                - For 1D resolution all PnL values are calculated relative to the base_value, we are not reseting the base value.
            
            - end (datetime) : The timestamp the data is returned up to in RFC3339 format (including timezone specification).

                - For timeframes less than 1D, the actual start will be determined based on the value of the intraday_reporting query parameter:
                - For example if the intraday_reporting is extended_hours, and the timestamp specified is 2023-10-19T21:33:00-04:00, then the last
                    data point returned will be 2023-10-19T20:00:00-04:00 due to the session closing at that time.
                    start, end (or date_end) and period cannot be specified at the same time.
                - If unset, the current time is considered the end's default value.
            
            - cashflow_types (str) : The cashflow activities to include in the report. One of 'ALL', 'NONE', or a comma-separated list of activity types.
         """

        if period and start and end:
            raise ParameterConflictError("Only two of start, end (or date_end) and period can be specified at the same time.")

        params = {}
        # --- Build request params ---
        if period:
            params["period"] = str(period)
        if timeframe:
            params["timeframe"] = timeframe
        if intraday_reporting:
            params["intraday_reporting"] = str(intraday_reporting)
        if start:
            params["start"] = str(start)
        if pnl_reset:
            params["pnl_reset"] = str(pnl_reset)
        if end:
            params["end"] = end
        if cashflow_types:
            params["cashflow_types"] = cashflow_types
                
        response = await self.get(
            endpoint="account/portfolio/history",
            params=params
        )
        
        return PortfolioPerformance.from_raw(response)
            