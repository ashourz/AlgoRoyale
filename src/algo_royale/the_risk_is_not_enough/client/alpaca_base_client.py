## client\alpaca_base_client.py
from abc import ABC, abstractmethod
import asyncio
from enum import Enum
from datetime import date, datetime
from typing import Any, Dict, Optional
from algo_royale.the_risk_is_not_enough.client.exceptions import AlpacaAPIException, AlpacaBadRequestException, AlpacaInvalidHeadersException, AlpacaResourceNotFoundException, AlpacaServerErrorException, AlpacaTooManyRequestsException, AlpacaUnauthorizedException, AlpacaUnprocessableException
import httpx
from algo_royale.the_risk_is_not_enough.config.config import ALPACA_PARAMS, ALPACA_SECRETS
from algo_royale.shared.logger.logger_singleton import Environment, LoggerSingleton, LoggerType
import time

class AlpacaBaseClient(ABC):
    """Async-only base client with global rate limiting"""
    _instance = None
    _lock = asyncio.Lock()
    _min_request_interval: float = 60 / 200  # 0.3 seconds between requests
    _last_request_time: float = 0
    _rate_limit_lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            # If there's no instance, create one
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        else:
            # If instance exists, check if the client is closed and reopen if necessary
            if hasattr(cls._instance, 'client') and cls._instance.client.is_closed:
                cls._instance.client = httpx.AsyncClient(timeout=10.0)
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
        
        self.client = httpx.AsyncClient(timeout=10.0)

        # Configurable reconnect delay and keep-alive timeout
        self.reconnect_delay = ALPACA_PARAMS.get("reconnect_delay", 5)
        self.keep_alive_timeout = ALPACA_PARAMS.get("keep_alive_timeout", 20)

        self.logger = LoggerSingleton(LoggerType.TRADING, Environment.PRODUCTION).get_logger()

    async def aclose(self):
        """Proper async cleanup"""
        if hasattr(self, 'client'):
            if not self.client.is_closed:
                await self.client.aclose()
                self.logger.debug(f"Closed {self.client_name} HTTP client")
            # Ensure client can't be reused
            del self.clients
        
    async def __aenter__(self):
        """Support async context manager"""
        if not hasattr(self, 'client') or self.client.is_closed:
            self.client = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, *exc_info):
        """Auto-close on context exit"""
        await self.aclose()
        
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
            self.api_key_header: self.api_key,
            self.api_secret_header: self.api_secret,
        }
    
    def _handle_http_error(self, response: httpx.Response) -> None:
        """Handle HTTP error responses."""
        if response.status_code == 400:
            raise AlpacaBadRequestException(response.text)
        elif response.status_code == 401:
            raise AlpacaUnauthorizedException(response.text)
        elif response.status_code == 403:
            raise AlpacaInvalidHeadersException(response.text)
        elif response.status_code == 404:
            raise AlpacaResourceNotFoundException(response.text)
        elif response.status_code == 422:
            raise AlpacaUnprocessableException(response.text)
        elif response.status_code == 429:
            limit = response.headers["X-RateLimit-Limit"]
            remaining = response.headers["X-RateLimit-Remaining"]
            reset = response.headers["X-RateLimit-Reset"]
            raise AlpacaTooManyRequestsException(
                message=response.text,
                limit=limit, 
                remaining=remaining, 
                reset=reset)
        elif response.status_code >= 500:
            raise AlpacaServerErrorException(f"Server error: {response.text}", response.status_code)
        elif not (200 <= response.status_code < 300):
            raise AlpacaAPIException(f"Unexpected error: {response.text}", response.status_code)

    def _format_param(self, param: Any) -> Any:
        """Format parameter for API requests."""
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

    def _format_data(self, param: Any) -> Any:
        """Format parameter for API requests."""
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
        # elif isinstance(param, bool):
            # return str(param).lower()
        elif param is None:
            return None
        else:
            return str(param)
      
    def _safe_json_parse(self, response: httpx.Response) -> Any:
        """Safely parse a JSON response or return None if not applicable."""
        try:
            if 200 <= response.status_code < 300 and not response.text.strip():
                return None
            return response.json()
        except ValueError:
            self.logger.warning(f"Unable to parse JSON from response: {response.text}")
            return None
        
    async def _enforce_rate_limit(self):
        """Global rate limiter shared across all clients"""
        async with self._rate_limit_lock:
            elapsed = time.time() - self._last_request_time
            if elapsed < self._min_request_interval:
                await asyncio.sleep(self._min_request_interval - elapsed)
            self._last_request_time = time.time()

    async def _make_request_async(self, 
                                  method: str, 
                                  endpoint: str, 
                                  params: Optional[Dict] = None, 
                                  data: Optional[Dict] = None) -> Any:
        """Core async request method with rate limiting"""
        await self._enforce_rate_limit()
        # Format parameters with option to skip
        formatted_params = {key: self._format_param(value) for key, value in (params or {}).items()}
        formatted_data = {key: self._format_data(value) for key, value in (data or {}).items()}
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        # Logging the request before sending
        self.logger.debug(
            f"sending {method.upper()} request to {url} | headers: {headers} | params: {formatted_params} | data: {formatted_data}"
        )
        
        response = await self.client.request(method=method, url = url,  headers = headers, params=formatted_params, json=data)

        self.logger.debug(
            f"received response {response.status_code} | body: {response.text}"
        )
        
        self._handle_http_error(response)
        response.raise_for_status()  # Will raise HTTPStatusError for 4xx/5xx errors
        return self._safe_json_parse(response)

    ## ASYNC
    async def get(self, endpoint: str, params: dict = None) -> Any:
        return await self._make_request_async("GET", endpoint, params=params)

    async def post(self, endpoint: str, params:dict =None, data: dict = None) -> Any:
        return await self._make_request_async("POST", endpoint, params=params, data=data)

    async def patch(self, endpoint: str, data: dict = None) -> Any:
        return await self._make_request_async("PATCH", endpoint, data=data)
    
    async def put(self, endpoint: str, params: dict = None, data: dict = None) -> Any:
        return await self._make_request_async("PUT", endpoint, params=params, data=data)

    async def delete(self, endpoint: str, params: dict = None) -> Any:
        return await self._make_request_async("DELETE", endpoint, params=params)