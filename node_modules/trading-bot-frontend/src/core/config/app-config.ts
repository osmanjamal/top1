export const APP_CONFIG = {
    // API Configuration
    api: {
      baseUrl: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000, // 30 seconds
      retryAttempts: 3,
      retryDelay: 1000, // 1 second
    },
  
    // WebSocket Configuration
    websocket: {
      url: process.env.REACT_APP_WS_URL || 'ws://localhost:8001',
      reconnectInterval: 3000,
      maxReconnectAttempts: 5
    },
  
    // Trading Configuration
    trading: {
      defaultLeverage: 10,
      maxLeverage: 100,
      defaultMarginType: 'isolated',
      maxPositionsPerSymbol: 10,
      maxTotalPositions: 50,
      orderBookDepth: 20,
      priceUpdateInterval: 1000, // 1 second
      chartUpdateInterval: 5000, // 5 seconds
    },
  
    // Risk Management
    risk: {
      maxDrawdown: 50, // 50%
      dailyLossLimit: 20, // 20%
      marginCallThreshold: 80, // 80%
      maxAllowedSlippage: 1, // 1%
      defaultStopLossPercent: 5,
      defaultTakeProfitPercent: 10
    },
  
    // UI Configuration
    ui: {
      theme: 'dark',
      defaultLanguage: 'en',
      supportedLanguages: ['en', 'es', 'ar'],
      dateFormat: 'YYYY-MM-DD',
      timeFormat: 'HH:mm:ss',
      decimalPrecision: {
        price: 2,
        amount: 6,
        percentage: 2
      },
      pagination: {
        defaultPageSize: 10,
        pageSizeOptions: [10, 20, 50, 100]
      },
      notifications: {
        duration: 5000, // 5 seconds
        position: 'top-right'
      }
    },
  
    // Security Configuration
    security: {
      sessionTimeout: 3600000, // 1 hour
      maxLoginAttempts: 5,
      lockoutDuration: 900000, // 15 minutes
      passwordMinLength: 8,
      requireTwoFactor: true,
      jwtExpirationTime: 86400, // 24 hours
    },
  
    // Feature Flags
    features: {
      spotTrading: true,
      marginTrading: true,
      futuresTrading: true,
      stakingEnabled: false,
      signalBotEnabled: true,
      socialTradingEnabled: false,
      demoTradingEnabled: true
    },
  
    // Error Handling
    errors: {
      logLevel: 'error', // 'debug' | 'info' | 'warn' | 'error'
      reportToServer: true,
      showDetailsToUser: false
    },
  
    // Analytics
    analytics: {
      enabled: true,
      trackUserActions: true,
      trackErrors: true,
      trackPerformance: true
    }
  } as const;
  
  export type AppConfig = typeof APP_CONFIG;
  
  // Environment-specific overrides
  const environmentOverrides = {
    development: {
      api: {
        baseUrl: 'http://localhost:8000',
      },
      security: {
        requireTwoFactor: false
      },
      errors: {
        showDetailsToUser: true
      }
    },
    production: {
      api: {
        baseUrl: process.env.REACT_APP_API_BASE_URL,
      },
      security: {
        requireTwoFactor: true
      },
      errors: {
        showDetailsToUser: false
      }
    },
    test: {
      api: {
        baseUrl: 'http://localhost:8000',
      },
      security: {
        requireTwoFactor: false
      }
    }
  };
  
  // Apply environment-specific overrides
  const env = process.env.NODE_ENV || 'development';
  export const config: AppConfig = {
    ...APP_CONFIG,
    ...environmentOverrides[env as keyof typeof environmentOverrides]
  };