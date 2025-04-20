# alpaca_client/exceptions.py

class OrderError(Exception):
    """Base class for order-related errors."""
    pass

class MissingParameterError(OrderError):
    """Raised when a required parameter is missing."""
    pass

class ParameterConflictError(OrderError):
    """Raised when mutually exclusive parameters are provided."""
    pass

class InvalidOrderError(OrderError):
    """Raised when an invalid value is given for an order parameter."""
    pass

class InsufficientBuyingPowerError(OrderError):
    """Raised when user has insufficient funds to place order."""
    pass

class InsufficientSharesError(OrderError):
    """Raised when user attempts to sell more shares than they own."""
    pass