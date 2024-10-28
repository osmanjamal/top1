export enum OrderSide {
    BUY = 'BUY',
    SELL = 'SELL'
  }
  
  export enum OrderType {
    MARKET = 'MARKET',
    LIMIT = 'LIMIT',
    STOP_MARKET = 'STOP_MARKET',
    STOP_LIMIT = 'STOP_LIMIT',
    TAKE_PROFIT_MARKET = 'TAKE_PROFIT_MARKET',
    TAKE_PROFIT_LIMIT = 'TAKE_PROFIT_LIMIT'
  }
  
  export enum OrderStatus {
    NEW = 'NEW',
    PARTIALLY_FILLED = 'PARTIALLY_FILLED',
    FILLED = 'FILLED',
    CANCELED = 'CANCELED',
    EXPIRED = 'EXPIRED',
    REJECTED = 'REJECTED'
  }
  
  export enum TimeInForce {
    GTC = 'GTC', // Good Till Cancel
    IOC = 'IOC', // Immediate or Cancel
    FOK = 'FOK'  // Fill or Kill
  }
  
  export interface OrderBase {
    id: string;
    clientOrderId?: string;
    symbol: string;
    side: OrderSide;
    type: OrderType;
    status: OrderStatus;
    quantity: number;
    price?: number;
    stopPrice?: number;
    created_at: Date;
    updated_at: Date;
  }
  
  export interface SpotOrder extends OrderBase {
    quoteOrderQty?: number;
    icebergQty?: number;
    timeInForce?: TimeInForce;
  }
  
  export interface FuturesOrder extends OrderBase {
    reduceOnly: boolean;
    closePosition: boolean;
    leverage: number;
    marginType: 'isolated' | 'crossed';
    positionSide: 'LONG' | 'SHORT' | 'BOTH';
    workingType: 'MARK_PRICE' | 'CONTRACT_PRICE';
    priceProtect: boolean;
    activatePrice?: number;
    callbackRate?: number;
  }
  
  export interface OrderCreate {
    symbol: string;
    side: OrderSide;
    type: OrderType;
    quantity: number;
    price?: number;
    stopPrice?: number;
    timeInForce?: TimeInForce;
    reduceOnly?: boolean;
    closePosition?: boolean;
    leverage?: number;
    workingType?: 'MARK_PRICE' | 'CONTRACT_PRICE';
  }
  
  export interface OrderResponse {
    orderId: string;
    symbol: string;
    status: OrderStatus;
    clientOrderId: string;
    price: string;
    avgPrice: string;
    origQty: string;
    executedQty: string;
    cumQuote: string;
    timeInForce: TimeInForce;
    type: OrderType;
    side: OrderSide;
    stopPrice?: string;
    time: number;
    updateTime: number;
  }
  
  export interface OrderBook {
    lastUpdateId: number;
    bids: [string, string][]; // [price, quantity][]
    asks: [string, string][]; // [price, quantity][]
  }
  
  export interface OrderUpdate {
    orderId: string;
    symbol: string;
    status: OrderStatus;
    price?: number;
    quantity?: number;
    stopPrice?: number;
  }
  
  export interface OrderFilter {
    symbol?: string;
    side?: OrderSide;
    status?: OrderStatus;
    type?: OrderType;
    startTime?: Date;
    endTime?: Date;
    limit?: number;
  }
  
  export interface OrderExecutionReport {
    symbol: string;
    orderId: string;
    orderListId: number;
    clientOrderId: string;
    transactTime: number;
    price: string;
    origQty: string;
    executedQty: string;
    cummulativeQuoteQty: string;
    status: OrderStatus;
    timeInForce: TimeInForce;
    type: OrderType;
    side: OrderSide;
    stopPrice?: string;
    workingTime: number;
    selfTradePreventionMode: string;
  }
  
  export interface OrderSummary {
    totalOrders: number;
    openOrders: number;
    filledOrders: number;
    canceledOrders: number;
    averageFillRate: number;
    totalVolume: number;
    totalFees: number;
  }
  
  export interface BatchOrderRequest {
    orders: OrderCreate[];
    validateOnly?: boolean;
  }
  
  export interface BatchOrderResponse {
    orders: OrderResponse[];
    validationErrors?: string[];
  }