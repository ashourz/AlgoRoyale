import asyncio
import time
from abc import ABC, abstractmethod
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional

import httpx

from algo_royale.clients.alpaca.exceptions import (
    AlpacaAPIException,
    AlpacaBadRequestException,
    AlpacaInvalidHeadersException,
    AlpacaResourceNotFoundException,
    AlpacaServerErrorException,
    AlpacaTooManyRequestsException,
    AlpacaUnauthorizedException,
    AlpacaUnprocessableException,
)
from algo_royale.logging.loggable import Loggable


class AlpacaBaseClient(ABC):
    """Async-only base client with global rate limiting across instances"""

    # Class-level variables for shared rate limiting
    _min_request_interval: float = 60 / 200  # 0.3 seconds between requests
    _last_request_time: float = 0
    _rate_limit_lock: asyncio.Lock = asyncio.Lock()

    def __init__(
        self,
        logger: Loggable,
        base_url: str,
        api_key: str,
        api_secret: str,
        api_key_header: str,
        api_secret_header: str,
        http_timeout: int = 10,
        reconnect_delay: int = 5,
        keep_alive_timeout: int = 20,
    ):
        # Instance-specific initialization
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_key_header = api_key_header
        self.api_secret_header = api_secret_header
        self.http_timeout = http_timeout

        self.client = httpx.AsyncClient(timeout=http_timeout)

        # Configurable reconnect delay and keep-alive timeout
        self.reconnect_delay = reconnect_delay
        self.keep_alive_timeout = keep_alive_timeout

        self.logger = logger

    async def aclose(self):
        """Proper async cleanup"""
        if hasattr(self, "client") and not self.client.is_closed:
            await self.client.aclose()
            self.logger.debug(f"Closed {self.client_name} HTTP client")

    async def __aenter__(self):
        """Support async context manager"""
        if not hasattr(self, "client") or self.client.is_closed:
            self.client = httpx.AsyncClient(timeout=self.http_timeout)
        return self

    async def __aexit__(self, *exc_info):
        """Auto-close on context exit"""
        await self.aclose()

    @property
    @abstractmethod
    def client_name(self) -> str:
        """Subclasses must define a name for logging and ID purposes"""
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
            limit = response.headers.get("X-RateLimit-Limit", "unknown")
            remaining = response.headers.get("X-RateLimit-Remaining", "unknown")
            reset = response.headers.get("X-RateLimit-Reset", "unknown")
            raise AlpacaTooManyRequestsException(
                message=response.text, limit=limit, remaining=remaining, reset=reset
            )
        elif response.status_code >= 500:
            raise AlpacaServerErrorException(
                f"Server error: {response.text}", response.status_code
            )
        elif not (200 <= response.status_code < 300):
            raise AlpacaAPIException(
                f"Unexpected error: {response.text}", response.status_code
            )

    def _format_param(self, param: Any) -> Any:
        """Format parameter for API requests."""
        if isinstance(param, datetime):
            return param.strftime("%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(param, date):
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

    def _safe_json_parse(self, response: httpx.Response) -> Any:
        """Safely parse a JSON response or return None if not applicable."""
        try:
            if 200 <= response.status_code < 300 and not response.text.strip():
                return None
            return response.json()
        except ValueError:
            self.logger.warning(f"Unable to parse JSON from response: {response.text}")
            return None

    @classmethod
    async def _enforce_rate_limit(cls):
        """Global rate limiter shared across all instances"""
        async with cls._rate_limit_lock:
            elapsed = time.time() - cls._last_request_time
            if elapsed < cls._min_request_interval:
                await asyncio.sleep(cls._min_request_interval - elapsed)
            cls._last_request_time = time.time()

    async def _make_request_async(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Any:
        """Core async request method with rate limiting"""
        await self._enforce_rate_limit()
        formatted_params = {
            key: self._format_param(value) for key, value in (params or {}).items()
        }
        formatted_data = {
            key: self._format_param(value) for key, value in (data or {}).items()
        }
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()

        self.logger.debug(
            f"sending {method.upper()} request to {url} | headers: {headers} | params: {formatted_params} | data: {formatted_data}"
        )

        response = await self.client.request(
            method=method, url=url, headers=headers, params=formatted_params, json=data
        )

        self.logger.debug(
            f"received response {response.status_code} | body: {response.text}"
        )

        self._handle_http_error(response)
        response.raise_for_status()  # Will raise HTTPStatusError for 4xx/5xx errors
        return self._safe_json_parse(response)

    def _ensure_client_open(self):
        if not hasattr(self, "client") or self.client.is_closed:
            self.client = httpx.AsyncClient(timeout=self.http_timeout)

    ## ASYNC
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Async GET request with rate limiting"""
        self._ensure_client_open()
        return await self._make_request_async("GET", endpoint, params=params)

    async def post(
        self, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Any:
        """Async POST request with rate limiting"""
        self._ensure_client_open()
        return await self._make_request_async(
            "POST", endpoint, params=params, data=data
        )

    async def patch(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """Async PATCH request with rate limiting"""
        self._ensure_client_open()
        return await self._make_request_async("PATCH", endpoint, data=data)

    async def put(
        self, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Any:
        """Async PUT request with rate limiting"""
        self._ensure_client_open()
        return await self._make_request_async("PUT", endpoint, params=params, data=data)

    async def delete(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Async DELETE request with rate limiting"""
        self._ensure_client_open()
        return await self._make_request_async("DELETE", endpoint, params=params)
