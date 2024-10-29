export const EXCHANGE_CONFIG = {
    binance: {
      // API Configuration
      api: {
        spot: {
          baseUrl: 'https://api.binance.com',
          testnetUrl: 'https://testnet.binance.vision',
          websocketUrl: 'wss://stream.binance.com:9443/ws',
          apiVersion: 'v3'
        },
        futures: {
          baseUrl: 'https://fapi.binance.com',
          testnetUrl: 'https://testnet.binancefuture.com',
          websocketUrl: 'wss://fstream.binance.com/ws',
          apiVersion: 'v1'
        }
      },
  
      // Rate Limits
      rateLimits: {
        orders: {
          maxPerSecond: 10,
          maxPerMinute: 1200,
          maxPerDay: 100000
        },
        requestWeight: {
          maxPerMinute: 1200,
          orderWeight: 1,
          accountInfoWeight: 5,
          tradesHistoryWeight: 5
        }
      },
  
      // Trading Parameters
      trading: {
        spot: {
          minOrderSize: 10, // USDT
          maxOrderSize: 1000000, // USDT
          defaultFees: {
            maker: 0.001, // 0.1%
            taker: 0.001  // 0.1%
          },
          allowedOrderTypes: ['LIMIT', 'MARKET', 'STOP_LOSS', 'TAKE_PROFIT']
        },
        futures: {
          minOrderSize: 5, // USDT
          maxOrderSize: 5000000, // USDT
          maxLeverage: 125,
          defaultFees: {
            maker: 0.0002, // 0.02%
            taker: 0.0004  // 0.04%
          },
          allowedOrderTypes: [
            'LIMIT',
            'MARKET',
            'STOP',
            'STOP_MARKET',
            'TAKE_PROFIT',
            'TAKE_PROFIT_MARKET'
          ]
        }
      },
  
      // Symbol Configurations
      symbols: {
        'BTCUSDT': {
          baseAsset: 'BTC',
          quoteAsset: 'USDT',
          pricePrecision: 2,
          quantityPrecision: 6,
          minQuantity: 0.000001,
          maxQuantity: 9000,
          minPrice: 0.01,
          maxPrice: 1000000,
          tickSize: 0.01,
          stepSize: 0.000001,
          allowedMarginLeverage: [1, 3, 5, 10, 25, 50, 75, 100, 125]
        },
        'ETHUSDT': {
          baseAsset: 'ETH',
          quoteAsset: 'USDT',
          pricePrecision: 2,
          quantityPrecision: 5,
          minQuantity: 0.00001,
          maxQuantity: 100000,
          minPrice: 0.01,
          maxPrice: 100000,
          tickSize: 0.01,
          stepSize: 0.00001,
          allowedMarginLeverage: [1, 3, 5, 10, 25, 50, 75, 100, 125]
        }
      },
  
      // Error Codes and Messages
      errors: {
        INSUFFICIENT_BALANCE: -1013,
        PRICE_QTY_EXCEED_HARD_LIMITS: -1021,
        INVALID_TIMESTAMP: -1021,
        INVALID_SIGNATURE: -1022,
        UNKNOWN_ORDER_COMPOSITION: -1032,
        TOO_MANY_ORDERS: -1429,
        BREAK_PRICE_PROTECTION: -2019
      },
  
      // Websocket Configuration
      websocket: {
        reconnectInterval: 5000,
        maxReconnectAttempts: 5,
        pingInterval: 30000,
        defaultSubscriptions: ['ticker', 'trades', 'kline_1m'],
        bufferSize: 1000
      }
    }
  } as const;
  
  // Utility types for type safety
  export type ExchangeConfig = typeof EXCHANGE_CONFIG;
  export type SupportedExchange = keyof typeof EXCHANGE_CONFIG;
  export type SymbolConfig = typeof EXCHANGE_CONFIG.binance.symbols.BTCUSDT;
  
  // Get configuration for a specific exchange
  export const getExchangeConfig = (exchange: SupportedExchange) => {
    return EXCHANGE_CONFIG[exchange];
  };
  
  // Get symbol configuration
  export const getSymbolConfig = (
    exchange: SupportedExchange,
    symbol: string
  ): SymbolConfig | undefined => {
    return EXCHANGE_CONFIG[exchange].symbols[symbol as keyof typeof EXCHANGE_CONFIG.binance.symbols];
  };