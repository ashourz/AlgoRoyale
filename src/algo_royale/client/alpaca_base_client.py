# src/algo_royale/client/alpaca_base_client.py
from abc import ABC, abstractmethod
import asyncio
from enum import Enum
import logging
from datetime import date, datetime
from typing import Any, Dict
from algo_royale.client.exceptions import AlpacaAPIException, AlpacaBadRequestException, AlpacaServerErrorException, AlpacaUnauthorizedException
import httpx
from config.config import ALPACA_PARAMS, ALPACA_SECRETS, LOGGING_PARAMS, get_logging_level

class AlpacaBaseClient(ABC):
    """Singleton class to interact with Alpaca's API"""
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        # continue with initialization...
        self.api_key = ALPACA_SECRETS["api_key"]
        self.api_secret = ALPACA_SECRETS["api_secret"]        
        self.api_key_header = ALPACA_PARAMS["api_key_header"]
        self.api_secret_header = ALPACA_PARAMS["api_secret_header"]
        
        self.client = httpx.Client(timeout=10.0)  # or httpx.AsyncClient(...) if using asyncio
        self.async_client = httpx.AsyncClient(timeout=10.0)

        # Configurable reconnect delay and keep-alive timeout
        self.reconnect_delay = ALPACA_PARAMS.get("reconnect_delay", 5)
        self.keep_alive_timeout = ALPACA_PARAMS.get("keep_alive_timeout", 20)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(get_logging_level())    

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
    @property
    @abstractmethod
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL for the Alpaca API (to be defined by subclass)"""
        pass
    
    def _get_headers(self) -> Dict[str, str]:
        """Return headers needed for API requests."""
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
        }
    
    def _handle_http_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses."""
        if response.status_code == 400:
            raise AlpacaBadRequestException(f"Bad request: {response.text}", 400)
        elif response.status_code == 401:
            raise AlpacaUnauthorizedException(f"Unauthorized access: {response.text}")
        elif response.status_code == 403:
            raise AlpacaAPIException(f"Forbidden: {response.text}", 403)
        elif response.status_code == 404:
            raise AlpacaAPIException(f"Resource not found: {response.text}", 404)
        elif response.status_code == 422:
            raise AlpacaAPIException(f"Unprocessable Entity: {response.text}", 422)
        elif response.status_code >= 500:
            raise AlpacaServerErrorException(f"Server error: {response.text}", response.status_code)
        elif not response.is_success:
            raise AlpacaAPIException(f"Unexpected error: {response.text}", response.status_code)

    def _format_param(self, param: Any, skip_format: bool = False) -> Any:
        """Format parameter for API requests with option to skip formatting."""
        if skip_format:
            return param  # If skip_format is True, return the param as-is.

        if isinstance(param, datetime):
            # Format to ISO 8601 with Zulu time
            return param.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(param, date):
            # Format to ISO 8601 with Zulu time
            return param.strftime("%Y-%m-%d")
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

    def _make_request(self, method: str, endpoint: str, params: dict = None, data: dict = None, skip_format: bool = False) -> Any:
        """General method for making HTTP requests to the Alpaca API."""
        try:
            # Format parameters with option to skip
            formatted_params = {key: self._format_param(value, skip_format) for key, value in (params or {}).items()}
            formatted_data = {key: self._format_param(value, skip_format) for key, value in (data or {}).items()}
            url = f"{self.base_url}/{endpoint}"
            headers = self._get_headers()

            # Logging the request before sending
            self.logger.debug(
                f"sending {method.upper()} request to {url} | headers: {headers} | params: {formatted_params} | data: {formatted_data}"
            )

            response = self.client.request(method, url, params=formatted_params, json=formatted_data)
            
            self.logger.debug(
                f"received response {response.status_code} | body: {response.text}"
            )
            
            response.raise_for_status()  # Will raise HTTPStatusError for 4xx/5xx errors
            self._handle_http_error(response)
            return response.json()
        except httpx.HTTPStatusError as e:
            raise AlpacaAPIException(f"HTTP status error: {e}")
        except Exception as e:
            raise AlpacaAPIException(f"An unexpected error occurred: {e}")

    async def _make_request_async(self, method: str, endpoint: str, params: dict = None, data: dict = None, skip_format: bool = False) -> Any:
        """General method for making HTTP requests to the Alpaca API."""
        try:
            # Format parameters with option to skip
            formatted_params = {key: self._format_param(value, skip_format) for key, value in (params or {}).items()}
            formatted_data = {key: self._format_param(value, skip_format) for key, value in (data or {}).items()}
            url = f"{self.base_url}/{endpoint}"
            headers = self._get_headers()

            # Logging the request before sending
            self.logger.debug(
                f"sending {method.upper()} request to {url} | headers: {headers} | params: {formatted_params} | data: {formatted_data}"
            )
            
            response = await self.async_client.request(method, url, params=formatted_params, json=formatted_data)
            
            self.logger.debug(
                f"received response {response.status_code} | body: {response.text}"
            )
            
            response.raise_for_status()  # Will raise HTTPStatusError for 4xx/5xx errors
            self._handle_http_error(response)
            return response.json()
        except httpx.HTTPStatusError as e:
            raise AlpacaAPIException(f"HTTP status error: {e}")
        except Exception as e:
            raise AlpacaAPIException(f"An unexpected error occurred: {e}")
        
    ## SYNC
    def get(self, endpoint: str, params: dict = None, skip_format: bool = False) -> Any:
        return self._make_request("GET", endpoint, params=params, skip_format=skip_format)

    def post(self, endpoint: str, data: dict = None, skip_format: bool = False) -> Any:
        return self._make_request("POST", endpoint, data=data, skip_format=skip_format)

    def put(self, endpoint: str, data: dict = None, skip_format: bool = False) -> Any:
        return self._make_request("PUT", endpoint, data=data, skip_format=skip_format)

    def delete(self, endpoint: str, params: dict = None, skip_format: bool = False) -> Any:
        return self._make_request("DELETE", endpoint, params=params, skip_format=skip_format)
    
    ## ASYNC
    def get_async(self, endpoint: str, params: dict = None, skip_format: bool = False) -> Any:
        return self._make_request_async("GET", endpoint, params=params, skip_format=skip_format)

    def post_async(self, endpoint: str, data: dict = None, skip_format: bool = False) -> Any:
        return self._make_request_async("POST", endpoint, data=data, skip_format=skip_format)

    def put_async(self, endpoint: str, data: dict = None, skip_format: bool = False) -> Any:
        return self._make_request_async("PUT", endpoint, data=data, skip_format=skip_format)

    def delete_async(self, endpoint: str, params: dict = None, skip_format: bool = False) -> Any:
        return self._make_request_async("DELETE", endpoint, params=params, skip_format=skip_format)