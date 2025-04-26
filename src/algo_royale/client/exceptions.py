# alpaca_client/exceptions.py

## REQUEST EXCEPTION
class ClientRequestException(Exception):
    """ Base class for client request related errors."""
    def __init__(self, message: str = None):
        self.message = message
        super().__init__(self.message)

class MissingParameterError(ClientRequestException):
    """Raised when a required parameter is missing."""
    def __init__(self, message: str = None):
        super().__init__(message)

class ParameterConflictError(ClientRequestException):
    """Raised when mutually exclusive parameters are provided."""
    def __init__(self, message: str = None):
        super().__init__(message)

## RESPONSE EXCEPTIONS
class AlpacaAPIException(Exception):
    """Base exception for Alpaca API errors."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AlpacaBadRequestException(AlpacaAPIException):
    """Exception for Bad Request (400)."""
    def __init__(self, message: str = None, status_code: int = 400):
        super().__init__(message, status_code)

class AlpacaUnauthorizedException(AlpacaAPIException):
    """Exception for Unauthorized (401)."""
    def __init__(self, message: str = None, status_code: int = 401):
        super().__init__(message, status_code)

class AlpacaInvalidHeadersException(AlpacaAPIException):
    """Exception for Missing or Invalid Headers (403)."""
    def __init__(self, message: str = None, status_code: int = 403):
        super().__init__(message, status_code)
        
class AlpacaResourceNotFoundException(AlpacaAPIException):
    """Exception for Resource not found (404)."""
    def __init__(self, message: str = None, status_code: int = 404):
        super().__init__(message, status_code)
        
class AlpacaUnprocessableException(AlpacaAPIException):
    """Exception for Input parameters are not recognized (422)."""
    def __init__(self, message: str = None, status_code: int = 422):
        super().__init__(message, status_code)
        
class AlpacaTooManyRequestsException(AlpacaAPIException):
    """Exception for Server Error (429). Too many requests. You hit the rate limit.
    
    Attributes:
        - limit (int) :Request limit per minute.
        - remaining (int) : Request limit per minute remaining.
        - reset (int) : The UNIX epoch when the remaining quota changes.
    """
    def __init__(self, message: str = None, status_code: int = 429, limit: int = None, remaining: int = None, reset: int = None):
        self.limit = limit
        self.remaining = remaining
        self.reset = reset
        super().__init__(message, status_code)

class AlpacaServerErrorException(AlpacaAPIException):
    """Exception for Server Error (500+)."""
    def __init__(self, message: str = None, status_code: int = 500):
        super().__init__(message, status_code)

## ORDERS
class AlpacaOrderException(AlpacaAPIException):
    """Base class for order-related errors."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message, status_code)

class InsufficientBuyingPowerOrSharesError(AlpacaOrderException):
    """Raised when user has insufficient buying power or shares on POST request."""
    def __init__(self, message: str = None, status_code = 403):
        super().__init__(message, status_code)

class UnprocessableOrderException(AlpacaOrderException):
    """Raised when the order status is not cancelable on DELETE request. (422)."""
    def __init__(self, message: str = None, status_code: int = 422):
        super().__init__(message, status_code)

## ASSETS
class AlpacaAssetNotFoundException(AlpacaAPIException):
    """Raised when Asset object is not found on GET request (404)."""
    def __init__(self, message: str = None, status_code: int = 404):
        super().__init__(message, status_code)
        
## WATCHLIST
class AlpacaWatchlistNotFoundException(AlpacaAPIException):
    """Raised when Watchlist object is not found on DELETE by Id request (404)."""
    def __init__(self, message: str = None, status_code: int = 404):
        super().__init__(message, status_code)
        
## POSITION
class AlpacaPositionNotFoundException(AlpacaAPIException):
    """Raised when Position object is not found on GET or DELETE by Id request (404)."""
    def __init__(self, message: str = None, status_code: int = 404):
        super().__init__(message, status_code)