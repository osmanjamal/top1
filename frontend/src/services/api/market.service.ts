import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';

interface Ticker {
  symbol: string;
  lastPrice: number;
  high24h: number;
  low24h: number;
  volume24h: number;
  change24h: number;
  changePercent24h: number;
}

interface OrderBookLevel {
  price: number;
  amount: number;
  total: number;
}

interface OrderBook {
  symbol: string;
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  timestamp: number;
}

interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  price: number;
  amount: number;
  timestamp: number;
}

interface Candle {
  timestamp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

class MarketService {
  // Ticker Data
  async getTicker(symbol: string): Promise<Ticker> {
    try {
      const response = await apiClient.get<Ticker>(`${API_ENDPOINTS.MARKET.TICKER}/${symbol}`);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAllTickers(): Promise<Ticker[]> {
    try {
      const response = await apiClient.get<Ticker[]>(API_ENDPOINTS.MARKET.TICKER);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Order Book
  async getOrderBook(symbol: string, limit?: number): Promise<OrderBook> {
    try {
      const response = await apiClient.get<OrderBook>(
        `${API_ENDPOINTS.MARKET.ORDERBOOK}/${symbol}`,
        { params: { limit } }
      );
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Recent Trades
  async getTrades(symbol: string, params?: {
    limit?: number;
    from?: number;
    to?: number;
  }): Promise<Trade[]> {
    try {
      const response = await apiClient.get<Trade[]>(
        `${API_ENDPOINTS.MARKET.TRADES}/${symbol}`,
        { params }
      );
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Candlestick Data
  async getCandles(symbol: string, params: {
    interval: '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w';
    limit?: number;
    from?: number;
    to?: number;
  }): Promise<Candle[]> {
    try {
      const response = await apiClient.get<Candle[]>(
        `${API_ENDPOINTS.MARKET.CANDLES}/${symbol}`,
        { params }
      );
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (error.response) {
      const message = error.response.data?.message || 'Market data request failed';
      return new Error(message);
    }
    return new Error('Network error');
  }
}

export const marketService = new MarketService();

