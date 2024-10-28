from typing import Optional, Dict, Any

class BinanceError(Exception):
    """Base exception for Binance API errors."""
    
    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.response = response
        super().__init__(self.message)

class BinanceAPIError(BinanceError):
    """Exception for API request errors."""
    pass

class BinanceRequestError(BinanceError):
    """Exception for request formatting errors."""
    pass

class BinanceAuthError(BinanceError):
    """Exception for authentication errors."""
    pass

class BinanceOrderError(BinanceError):
    """Exception for order-related errors."""
    pass

class BinancePositionError(BinanceError):
    """Exception for position-related errors."""
    pass

class BinanceWebSocketError(BinanceError):
    """Exception for WebSocket connection errors."""
    pass

class BinanceRateLimitError(BinanceError):
    """Exception for rate limit errors."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        *args,
        **kwargs
    ):
        self.retry_after = retry_after
        super().__init__(message, *args, **kwargs)

class BinanceInvalidSymbolError(BinanceError):
    """Exception for invalid trading pair symbols."""
    pass

class BinanceInsufficientBalanceError(BinanceError):
    """Exception for insufficient balance errors."""
    
    def __init__(
        self,
        message: str,
        required_amount: Optional[float] = None,
        available_amount: Optional[float] = None,
        asset: Optional[str] = None,
        *args,
        **kwargs
    ):
        self.required_amount = required_amount
        self.available_amount = available_amount
        self.asset = asset
        super().__init__(message, *args, **kwargs)

class BinanceInvalidQuantityError(BinanceError):
    """Exception for invalid order quantity errors."""
    
    def __init__(
        self,
        message: str,
        min_qty: Optional[float] = None,
        max_qty: Optional[float] = None,
        step_size: Optional[float] = None,
        *args,
        **kwargs
    ):
        self.min_qty = min_qty
        self.max_qty = max_qty
        self.step_size = step_size
        super().__init__(message, *args, **kwargs)

class BinanceInvalidPriceError(BinanceError):
    """Exception for invalid price errors."""
    
    def __init__(
        self,
        message: str,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        tick_size: Optional[float] = None,
        *args,
        **kwargs
    ):
        self.min_price = min_price
        self.max_price = max_price
        self.tick_size = tick_size
        super().__init__(message, *args, **kwargs)

class BinanceLeverageError(BinanceError):
    """Exception for leverage-related errors."""
    
    def __init__(
        self,
        message: str,
        max_leverage: Optional[int] = None,
        *args,
        **kwargs
    ):
        self.max_leverage = max_leverage
        super().__init__(message, *args, **kwargs)

class BinanceMarginError(BinanceError):
    """Exception for margin-related errors."""
    pass

class BinancePositionModeError(BinanceError):
    """Exception for position mode errors."""
    pass

def handle_binance_error(response: Dict[str, Any]) -> None:
    """
    Handle Binance API error responses and raise appropriate exceptions.
    
    Args:
        response: Error response from Binance API
        
    Raises:
        appropriate BinanceError subclass
    """
    code = response.get('code')
    msg = response.get('msg', 'Unknown error')
    
    if code == -1001:  # Internal server error
        raise BinanceAPIError(f"Internal server error: {msg}", code, response)
    elif code == -1003:  # Too many requests
        raise BinanceRateLimitError(
            f"Rate limit exceeded: {msg}",
            retry_after=response.get('retryAfter'),
            code=code,
            response=response
        )
    elif code == -1010:  # Insufficient funds
        raise BinanceInsufficientBalanceError(
            f"Insufficient balance: {msg}",
            code=code,
            response=response
        )
    elif code == -1021:  # Timestamp outside of recv window
        raise BinanceRequestError(f"Invalid timestamp: {msg}", code, response)
    elif code == -1022:  # Invalid signature
        raise BinanceAuthError(f"Invalid signature: {msg}", code, response)
    elif code == -1100:  # Illegal characters in parameter
        raise BinanceRequestError(f"Invalid parameter: {msg}", code, response)
    elif code == -1111:  # Invalid quantity
        raise BinanceInvalidQuantityError(f"Invalid quantity: {msg}", code=code, response=response)
    elif code == -1112:  # Invalid order type
        raise BinanceOrderError(f"Invalid order type: {msg}", code, response)
    elif code == -1114:  # Invalid API key permissions
        raise BinanceAuthError(f"Invalid API key permissions: {msg}", code, response)
    elif code == -1115:  # Invalid API key
        raise BinanceAuthError(f"Invalid API key: {msg}", code, response)
    elif code == -1116:  # Invalid order status
        raise BinanceOrderError(f"Invalid order status: {msg}", code, response)
    elif code == -1117:  # Invalid price
        raise BinanceInvalidPriceError(f"Invalid price: {msg}", code=code, response=response)
    elif code == -1119:  # Invalid position side
        raise BinancePositionError(f"Invalid position side: {msg}", code, response)
    elif code == -1120:  # Invalid leverage
        raise BinanceLeverageError(f"Invalid leverage: {msg}", code=code, response=response)
    elif code == -1121:  # Invalid symbol
        raise BinanceInvalidSymbolError(f"Invalid symbol: {msg}", code, response)
    elif code == -1125:  # Invalid listen key
        raise BinanceWebSocketError(f"Invalid listen key: {msg}", code, response)
    elif code == -1130:  # Invalid order configuration
        raise BinanceOrderError(f"Invalid order configuration: {msg}", code, response)
    elif code == -2010:  # New order rejected
        raise BinanceOrderError(f"Order rejected: {msg}", code, response)
    elif code == -2011:  # Cancel order rejected
        raise BinanceOrderError(f"Cancel rejected: {msg}", code, response)
    elif code == -2013:  # No such order
        raise BinanceOrderError(f"Order not found: {msg}", code, response)
    elif code == -2014:  # Invalid API-key format
        raise BinanceAuthError(f"Invalid API key format: {msg}", code, response)
    elif code == -2015:  # Invalid API-key
        raise BinanceAuthError(f"Invalid API key: {msg}", code, response)
    elif code == -4001:  # Invalid margin type
        raise BinanceMarginError(f"Invalid margin type: {msg}", code, response)
    elif code == -4110:  # Invalid position mode
        raise BinancePositionModeError(f"Invalid position mode: {msg}", code, response)
    else:
        raise BinanceError(f"Unknown error: {msg}", code, response)