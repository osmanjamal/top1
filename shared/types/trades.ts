export enum TradeType {
    SPOT = 'SPOT',
    MARGIN = 'MARGIN',
    FUTURES = 'FUTURES'
  }
  
  export enum TradeSide {
    BUY = 'BUY',
    SELL = 'SELL'
  }
  
  export enum TradeStatus {
    PENDING = 'PENDING',
    EXECUTED = 'EXECUTED',
    FAILED = 'FAILED'
  }
  
  export interface Trade {
    id: string;
    userId: string;
    orderId?: string;
    positionId?: string;
    exchangeTradeId: string;
    symbol: string;
    type: TradeType;
    side: TradeSide;
    status: TradeStatus;
    price: number;
    quantity: number;
    commission?: number;
    commissionAsset?: string;
    realizedPnl?: number;
    quoteQuantity: number;
    
    // Timestamps
    executedAt: Date;
    createdAt: Date;
    updatedAt: Date;
  }
  
  export interface TradeHistory {
    trades: Trade[];
    summary: TradeSummary;
  }
  
  export interface TradeSummary {
    totalTrades: number;
    winningTrades: number;
    losingTrades: number;
    breakEvenTrades: number;
    profitFactor: number;
    averageWin: number;
    averageLoss: number;
    largestWin: number;
    largestLoss: number;
    winRate: number;
    volume: number;
    commission: number;
    netPnl: number;
  }
  
  export interface TradeFilter {
    symbol?: string;
    type?: TradeType;
    side?: TradeSide;
    startTime?: Date;
    endTime?: Date;
    minPrice?: number;
    maxPrice?: number;
    limit?: number;
  }
  
  export interface TradePerformance {
    trade: Trade;
    holdingTime: number;
    priceDeviation: number;
    slippage: number;
    executionSpeed: number;
    impact: number;
  }
  
  export interface TradeMetrics {
    entryPrice: number;
    exitPrice: number;
    volume: number;
    pnl: number;
    pnlPercentage: number;
    roe?: number;
    commission: number;
    slippage: number;
    duration: number;
  }
  
  export interface TradingPair {
    symbol: string;
    baseAsset: string;
    quoteAsset: string;
    pricePrecision: number;
    quantityPrecision: number;
    minQuantity: number;
    maxQuantity: number;
    minNotional: number;
    status: 'TRADING' | 'BREAK' | 'HALT';
  }
  
  export interface TradeExecution {
    trade: Trade;
    orderFills: OrderFill[];
    averagePrice: number;
    totalQuantity: number;
    totalValue: number;
    fees: TradeFees;
  }
  
  export interface OrderFill {
    price: number;
    quantity: number;
    timestamp: Date;
    fee: number;
    feeAsset: string;
  }
  
  export interface TradeFees {
    makerFee: number;
    takerFee: number;
    totalFees: number;
    feeAsset: string;
  }
  
  export interface TradeAlert {
    type: 'SLIPPAGE' | 'EXECUTION_DELAY' | 'LARGE_LOSS' | 'UNUSUAL_VOLUME';
    trade: Trade;
    threshold: number;
    currentValue: number;
    message: string;
    timestamp: Date;
  }
  
  export interface TradeAnalytics {
    profitLoss: {
      daily: number;
      weekly: number;
      monthly: number;
      total: number;
    };
    metrics: {
      winRate: number;
      profitFactor: number;
      sharpeRatio: number;
      maxDrawdown: number;
    };
    distribution: {
      byAsset: { [key: string]: number };
      byType: { [key: string]: number };
      byTimeOfDay: { [key: string]: number };
    };
    riskMetrics: {
      volatility: number;
      beta: number;
      correlation: number;
      valueAtRisk: number;
    };
  }
  
  export interface BatchTradeRequest {
    trades: Trade[];
    validateOnly?: boolean;
  }
  
  export interface BatchTradeResponse {
    trades: Trade[];
    validationErrors?: string[];
  }