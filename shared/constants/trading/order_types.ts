export const ORDER_SIDES = {
    BUY: 'BUY',
    SELL: 'SELL'
  } as const;
  
  export const ORDER_TYPES = {
    MARKET: 'MARKET',
    LIMIT: 'LIMIT',
    STOP_MARKET: 'STOP_MARKET',
    STOP_LIMIT: 'STOP_LIMIT',
    TAKE_PROFIT_MARKET: 'TAKE_PROFIT_MARKET',
    TAKE_PROFIT_LIMIT: 'TAKE_PROFIT_LIMIT'
  } as const;
  
  export const ORDER_STATUS = {
    NEW: 'NEW',
    PARTIALLY_FILLED: 'PARTIALLY_FILLED',
    FILLED: 'FILLED',
    CANCELED: 'CANCELED',
    PENDING_CANCEL: 'PENDING_CANCEL',
    REJECTED: 'REJECTED',
    EXPIRED: 'EXPIRED'
  } as const;
  
  export const TIME_IN_FORCE = {
    GTC: 'GTC', // Good Till Cancel
    IOC: 'IOC', // Immediate or Cancel
    FOK: 'FOK'  // Fill or Kill
  } as const;
  
  export const ORDER_RESPONSES = {
    ACK: 'ACK',         // Only confirmation of order receipt
    RESULT: 'RESULT',   // Full order details
    FULL: 'FULL'        // Full order details with fills
  } as const;
  
  export const ORDER_SOURCE = {
    API: 'API',
    WEB: 'WEB',
    MOBILE: 'MOBILE',
    BOT: 'BOT',
    AUTO_TRIGGER: 'AUTO_TRIGGER'
  } as const;
  
  export const ORDER_EXECUTION_TYPES = {
    NEW: 'NEW',
    CANCELED: 'CANCELED',
    REPLACED: 'REPLACED',
    REJECTED: 'REJECTED',
    TRADE: 'TRADE',
    EXPIRED: 'EXPIRED'
  } as const;
  
  export const ORDER_VALIDATION_RULES = {
    PRICE: {
      MIN_DISTANCE_PERCENT: 0.1,  // Minimum distance from current price
      MAX_DISTANCE_PERCENT: 500,  // Maximum distance from current price
      PRECISION: 8               // Maximum decimal places
    },
    QUANTITY: {
      MIN_NOTIONAL: 10,         // Minimum order value in USDT
      MAX_NOTIONAL: 1000000,    // Maximum order value in USDT
      PRECISION: 8              // Maximum decimal places
    },
    TIME: {
      MAX_OPEN_DURATION: 90,    // Maximum days an order can remain open
      MIN_CANCEL_INTERVAL: 1    // Minimum seconds between cancel requests
    }
  } as const;
  
  export const ORDER_DEFAULTS = {
    SPOT: {
      timeInForce: TIME_IN_FORCE.GTC,
      responseType: ORDER_RESPONSES.RESULT
    },
    FUTURES: {
      timeInForce: TIME_IN_FORCE.GTC,
      responseType: ORDER_RESPONSES.RESULT,
      workingType: 'MARK_PRICE',
      priceProtect: true,
      reduceOnly: false
    }
  } as const;
  
  export const ORDER_ERRORS = {
    UNKNOWN: 'Unknown error occurred',
    INVALID_SIDE: 'Invalid order side',
    INVALID_TYPE: 'Invalid order type',
    INVALID_QUANTITY: 'Invalid quantity',
    INVALID_PRICE: 'Invalid price',
    INSUFFICIENT_BALANCE: 'Insufficient balance',
    MIN_NOTIONAL: 'Order value is too small',
    MAX_NOTIONAL: 'Order value is too large',
    PRICE_FILTER: 'Price is outside allowed range',
    LOT_SIZE: 'Quantity is outside allowed range',
    MARKET_LOT_SIZE: 'Quantity is outside market limits',
    PERCENT_PRICE: 'Price is outside percent limits',
    MAX_NUM_ORDERS: 'Maximum number of orders reached',
    MAX_POSITION: 'Position size would exceed maximum allowed'
  } as const;
  
  export const ORDER_FLAGS = {
    POST_ONLY: 'POST_ONLY',
    REDUCE_ONLY: 'REDUCE_ONLY',
    CLOSE_POSITION: 'CLOSE_POSITION',
    OCO: 'OCO'
  } as const;
  
  export const PRICE_SOURCES = {
    LAST_PRICE: 'LAST_PRICE',
    MARK_PRICE: 'MARK_PRICE',
    INDEX_PRICE: 'INDEX_PRICE'
  } as const;