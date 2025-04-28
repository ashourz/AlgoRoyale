## client\alpaca_trading\alpaca_clock_client.py


from datetime import datetime
from typing import Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_trading.alpaca_calendar import CalendarList
from models.alpaca_trading.alpaca_clock import Clock
from models.alpaca_trading.enums import CalendarDateType
from config.config import ALPACA_TRADING_URL

class AlpacaClockClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for orders data.""" 

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaClockClient"    

    @property
    def base_url(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return ALPACA_TRADING_URL
    
    def fetch_clock(self) -> Optional[Clock]:
        """Fetch clock data from Alpaca."""

        response = self.get(
            endpoint="/clock"
        )    
        
        return Clock.from_raw(response)