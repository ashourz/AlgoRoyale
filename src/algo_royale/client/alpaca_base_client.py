# src/algo_royale/client/alpaca_base_client.py
from abc import ABC, abstractmethod
import asyncio
from enum import Enum
import logging
from datetime import datetime
import httpx
from config.config import ALPACA_PARAMS, ALPACA_SECRETS

class AlpacaBaseClient(ABC):
    """Singleton class to interact with Alpaca's API"""
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.api_key = ALPACA_SECRETS["api_key"]
        self.api_secret = ALPACA_SECRETS["api_secret"]        
        self.api_key_header = ALPACA_PARAMS["api_key_header"]
        self.api_secret_header = ALPACA_PARAMS["api_secret_header"]
        # Configurable reconnect delay and keep-alive timeout
        self.reconnect_delay = ALPACA_PARAMS.get("reconnect_delay", 5)
        self.keep_alive_timeout = ALPACA_PARAMS.get("keep_alive_timeout", 20)

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)    

        self.subscribed_symbols = set()

    @property
    @abstractmethod
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        pass
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def _format_param(self, param):
        if isinstance(param, datetime):
            # Format to ISO 8601 with Zulu time
            return param.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(param, Enum):
            return param.value
        elif isinstance(param, list):
            return ",".join(map(str, param))
        elif isinstance(param, bool):
            return str(param).lower()
        elif param is None:
            return None
        else:
            return str(param)

    def _get(
        self,
        url: str,
        includeHeaders: bool = True,
        params: dict = None,
    ):
        """Make a GET request to the Alpaca API."""
        if params is None:
            params = {}
        # Set the headers for authentication
        headers = {}
        if includeHeaders:
             headers ={ 
                self.api_key_header: self.api_key,
                self.api_secret_header: self.api_secret}        

        response = httpx.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def _post(
        self,
        url: str,
        includeHeaders: bool = True,
        payload: dict = None,
    ):
        """Make a POST request to the Alpaca API."""
        if payload is None:
            payload = {}
        # Set the headers for authentication
        headers = {}
        if includeHeaders:
             headers ={ 
                self.api_key_header: self.api_key,
                self.api_secret_header: self.api_secret}        

        response = httpx.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def _delete(
        self,
        url: str,
        includeHeaders: bool = True,
        payload: dict = None,
    ):
        """Make a POST request to the Alpaca API."""
        if payload is None:
            payload = {}
        # Set the headers for authentication
        headers = {}
        if includeHeaders:
             headers ={ 
                self.api_key_header: self.api_key,
                self.api_secret_header: self.api_secret}        

        response = httpx.delete(url, headers=headers)
        response.raise_for_status()
        return response.json()
    