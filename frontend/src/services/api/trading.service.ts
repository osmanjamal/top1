import { apiClient } from './client';
import { API_ENDPOINTS } from './endpoints';
import type { Order, Position } from './types';

interface CreateOrderRequest {
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit' | 'stop' | 'take_profit';
  price?: number;
  size: number;
  leverage?: number;
}

interface BalanceResponse {
  total: number;
  available: number;
  locked: number;
  pnl: {
    unrealized: number;
    realized: number;
  };
  margin: {
    used: number;
    free: number;
  };
}

class TradingService {
  // Orders management
  async getOrders(params?: { 
    symbol?: string; 
    status?: string; 
    limit?: number;
    from?: string;
    to?: string;
  }): Promise<Order[]> {
    try {
      const response = await apiClient.get<Order[]>(API_ENDPOINTS.TRADING.ORDERS, { params });
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createOrder(data: CreateOrderRequest): Promise<Order> {
    try {
      const response = await apiClient.post<Order>(API_ENDPOINTS.TRADING.ORDERS, data);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async cancelOrder(orderId: string): Promise<void> {
    try {
      await apiClient.delete(`${API_ENDPOINTS.TRADING.ORDERS}/${orderId}`);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Positions management
  async getPositions(params?: { 
    symbol?: string;
  }): Promise<Position[]> {
    try {
      const response = await apiClient.get<Position[]>(API_ENDPOINTS.TRADING.POSITIONS, { params });
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async closePosition(positionId: string, params?: {
    price?: number;
    type?: 'market' | 'limit';
  }): Promise<void> {
    try {
      await apiClient.post(`${API_ENDPOINTS.TRADING.POSITIONS}/${positionId}/close`, params);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateLeverage(symbol: string, leverage: number): Promise<void> {
    try {
      await apiClient.post(`${API_ENDPOINTS.TRADING.POSITIONS}/leverage`, {
        symbol,
        leverage
      });
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Balance information
  async getBalance(): Promise<BalanceResponse> {
    try {
      const response = await apiClient.get<BalanceResponse>(API_ENDPOINTS.TRADING.BALANCE);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Trading history
  async getTradeHistory(params?: {
    symbol?: string;
    from?: string;
    to?: string;
    limit?: number;
  }): Promise<any[]> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.TRADING.HISTORY, { params });
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (error.response) {
      const message = error.response.data?.message || 'Trading operation failed';
      return new Error(message);
    }
    return new Error('Network error');
  }
}

export const tradingService = new TradingService();
