export interface Balance {
  available: number;
  total: number;
  locked: number;
  unrealizedPnl: number;
}

export interface TradingAccount {
  id: string;
  userId: string;
  balances: Record<string, Balance>;
  marginLevel: number;
  totalEquity: number;
  usedMargin: number;
  freeMargin: number;
  leverage: number;
  updatedAt: string;
}

export interface Order {
  id: string;
  userId: string;
  symbol: string;
  type: 'market' | 'limit' | 'stop' | 'takeProfit';
  side: 'buy' | 'sell';
  price: number;
  amount: number;
  filled: number;
  remaining: number;
  status: 'pending' | 'open' | 'filled' | 'canceled' | 'rejected';
  createdAt: string;
  updatedAt: string;
}

export interface Position {
  id: string;
  userId: string;
  symbol: string;
  side: 'long' | 'short';
  entryPrice: number;
  amount: number;
  leverage: number;
  liquidationPrice: number;
  margin: number;
  unrealizedPnl: number;
  realizedPnl: number;
  status: 'open' | 'closed';
  createdAt: string;
  updatedAt: string;
}

export interface TradingState {
  account: TradingAccount | null;
  positions: Position[];
  orders: Order[];
  loading: {
    account: boolean;
    positions: boolean;
    orders: boolean;
  };
  error: string | null;
}

