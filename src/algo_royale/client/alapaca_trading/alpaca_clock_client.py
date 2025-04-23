# src/algo_royale/client/alpaca_corporate_action_client.py


from datetime import datetime
from typing import Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_trading.alpaca_calendar import CalendarList
from models.alpaca_trading.alpaca_clock import Clock
from models.alpaca_trading.enums import CalendarDateType
from config.config import ALPACA_TRADING_URL

class AlpacaClockClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for orders data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaClockClient"    
    
    def fetch_clock(self) -> Optional[Clock]:
        """Fetch clock data from Alpaca."""

        responseJson = self._get(
            url=f"{self.base_url}/clock"
        ).json()

        if responseJson is None:
            self._logger.warning(f"No clock data available")
            return None       
        
        return Clock.from_raw(responseJson)