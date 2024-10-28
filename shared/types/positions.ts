export enum PositionSide {
    LONG = 'LONG',
    SHORT = 'SHORT'
  }
  
  export enum PositionStatus {
    OPEN = 'OPEN',
    CLOSED = 'CLOSED',
    LIQUIDATED = 'LIQUIDATED'
  }
  
  export enum MarginType {
    ISOLATED = 'ISOLATED',
    CROSSED = 'CROSSED'
  }
  
  export interface Position {
    id: string;
    userId: string;
    symbol: string;
    side: PositionSide;
    status: PositionStatus;
    entryPrice: number;
    markPrice: number;
    liquidationPrice: number;
    size: number;
    leverage: number;
    marginType: MarginType;
    isolatedMargin?: number;
    
    // Risk management
    stopLoss?: number;
    takeProfit?: number;
    trailingStop?: number;
    
    // PnL tracking
    unrealizedPnl: number;
    realizedPnl: number;
    totalPnl: number;
    roe?: number;  // Return on Equity
    
    // Risk metrics
    riskRatio?: number;
    marginRatio?: number;
    
    // Timestamps
    openedAt: Date;
    updatedAt: Date;
    closedAt?: Date;
  }
  
  export interface PositionCreate {
    symbol: string;
    side: PositionSide;
    size: number;
    leverage: number;
    marginType: MarginType;
    stopLoss?: number;
    takeProfit?: number;
    trailingStop?: number;
  }
  
  export interface PositionUpdate {
    stopLoss?: number;
    takeProfit?: number;
    trailingStop?: number;
    leverage?: number;
    marginType?: MarginType;
  }
  
  export interface PositionRisk {
    entryPrice: number;
    markPrice: number;
    liquidationPrice: number;
    marginType: MarginType;
    isolatedMargin?: number;
    maintMargin: number;
    unrealizedPnl: number;
    marginRatio: number;
    leverage: number;
  }
  
  export interface PositionFilter {
    symbol?: string;
    side?: PositionSide;
    status?: PositionStatus;
    marginType?: MarginType;
    minLeverage?: number;
    maxLeverage?: number;
    startTime?: Date;
    endTime?: Date;
  }
  
  export interface PositionSummary {
    totalPositions: number;
    openPositions: number;
    closedPositions: number;
    liquidatedPositions: number;
    totalUnrealizedPnl: number;
    totalRealizedPnl: number;
    averageRoe: number;
    winRate: number;
  }
  
  export interface MarginInfo {
    maxLeverage: number;
    maintMarginRate: number;
    requiredMargin: number;
    isolatedMargin?: number;
    crossMargin?: number;
  }
  
  export interface PositionEvent {
    type: 'OPEN' | 'UPDATE' | 'CLOSE' | 'LIQUIDATION';
    position: Position;
    timestamp: Date;
    reason?: string;
  }
  
  export interface PositionMetrics {
    entryValue: number;
    currentValue: number;
    notionalValue: number;
    maintenanceMargin: number;
    marginRatio: number;
    leverage: number;
    effectiveLeverage: number;
    riskRatio: number;
    exposureRatio: number;
    profitLossRatio?: number;
  }
  
  export interface PositionRiskLimits {
    maxPositionSize: number;
    maxLeverage: number;
    maxDrawdown: number;
    maxMarginRatio: number;
    minMarginLevel: number;
  }
  
  export interface PositionPerformance {
    position: Position;
    holdingPeriod: number; // in milliseconds
    peakValue: number;
    drawdown: number;
    volatility: number;
    sharpeRatio?: number;
    profitFactor?: number;
  }
  
  export interface PositionHistoryItem {
    timestamp: Date;
    price: number;
    size: number;
    margin: number;
    pnl: number;
    roe: number;
    event: string;
  }
  
  export interface PositionAlert {
    type: 'MARGIN_CALL' | 'LIQUIDATION_WARNING' | 'HIGH_DRAWDOWN' | 'TAKE_PROFIT' | 'STOP_LOSS';
    position: Position;
    threshold: number;
    currentValue: number;
    message: string;
    timestamp: Date;
  }