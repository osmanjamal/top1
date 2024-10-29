export interface Signal {
    id: string;
    botId: string;
    name: string;
    symbol: string;
    timeframe: string;
    side: 'buy' | 'sell';
    price: number;
    status: 'pending' | 'executed' | 'failed' | 'canceled';
    metadata?: Record<string, any>;
    createdAt: string;
    executedAt?: string;
  }
  
  export interface Bot {
    id: string;
    userId: string;
    name: string;
    description?: string;
    strategy: {
      name: string;
      config: Record<string, any>;
    };
    symbols: string[];
    timeframes: string[];
    status: 'active' | 'paused' | 'stopped';
    stats: {
      totalSignals: number;
      successfulSignals: number;
      failedSignals: number;
      successRate: number;
      averageProfit: number;
    };
    createdAt: string;
    updatedAt: string;
  }
  
  export interface SignalExecution {
    id: string;
    signalId: string;
    orderId: string;
    entryPrice: number;
    exitPrice?: number;
    profit?: number;
    status: 'pending' | 'entered' | 'exited' | 'failed';
    metadata?: Record<string, any>;
    createdAt: string;
    updatedAt: string;
  }
  
  export interface SignalAlert {
    id: string;
    signalId: string;
    type: 'entry' | 'exit' | 'error';
    message: string;
    metadata?: Record<string, any>;
    createdAt: string;
    readAt?: string;
  }
  
  export interface SignalsState {
    bots: Bot[];
    activeSignals: Signal[];
    signalHistory: Signal[];
    loading: {
      bots: boolean;
      signals: boolean;
      history: boolean;
    };
    error: string | null;
  }
  
  export interface BotStatistics {
    daily: {
      signals: number;
      successRate: number;
      profit: number;
    };
    weekly: {
      signals: number;
      successRate: number;
      profit: number;
    };
    monthly: {
      signals: number;
      successRate: number;
      profit: number;
    };
    total: {
      signals: number;
      successRate: number;
      profit: number;
      runningDays: number;
    };
  }
  
  export interface BotSettings {
    riskManagement: {
      maxPositions: number;
      positionSize: number;
      stopLoss: number;
      takeProfit: number;
      maxDailyLoss: number;
    };
    notifications: {
      email: boolean;
      telegram: boolean;
      discord: boolean;
    };
    tradingHours: {
      enabled: boolean;
      start: string;
      end: string;
      timezone: string;
    };
    autoManagement: {
      enabled: boolean;
      adjustPositionSize: boolean;
      dynamicStopLoss: boolean;
      trailingStopLoss: boolean;
    };
  }
  