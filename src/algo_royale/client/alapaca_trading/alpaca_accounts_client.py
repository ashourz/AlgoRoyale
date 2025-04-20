# src/algo_royale/client/alpaca_news_client.py

from typing import List, Optional
from algo_royale.client.alpaca_base_client import AlpacaBaseClient
from models.alpaca_trading.alpaca_account import Account
from config.config import ALPACA_TRADING_URL

class AlpacaAccountClient(AlpacaBaseClient):
    """Singleton class to interact with Alpaca's API for news data.""" 
    
    def __init__(self):
        super().__init__()
        self.base_url = ALPACA_TRADING_URL

    @property
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        return "AlpacaNewsClient"    
    
    def fetch_account(self) -> Optional[Account]:
        """Fetch account data from Alpaca."""

        responseJson = self._get(
            url=f"{self.base_url}/account"
        ).json()

        # self._logger.debug(f"News for {symbols}: {responseJson}")
        if responseJson is None:
            self._logger.warning(f"No account data available")
            return None       
        
        return Account.from_raw(responseJson)


            