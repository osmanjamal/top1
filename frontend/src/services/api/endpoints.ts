export const API_ENDPOINTS = {
    AUTH: {
      LOGIN: '/auth/login',
      REGISTER: '/auth/register',
      LOGOUT: '/auth/logout',
      REFRESH_TOKEN: '/auth/refresh',
      VERIFY_EMAIL: '/auth/verify-email',
      RESET_PASSWORD: '/auth/reset-password',
      FORGOT_PASSWORD: '/auth/forgot-password',
    },
    USER: {
      PROFILE: '/user/profile',
      UPDATE_PROFILE: '/user/profile/update',
      CHANGE_PASSWORD: '/user/change-password',
      API_KEYS: '/user/api-keys',
    },
    TRADING: {
      ORDERS: '/trading/orders',
      POSITIONS: '/trading/positions',
      BALANCE: '/trading/balance',
      HISTORY: '/trading/history',
    },
    SIGNALS: {
      LIST: '/signals',
      CREATE: '/signals/create',
      UPDATE: '/signals/update',
      DELETE: '/signals/delete',
      STATS: '/signals/stats',
    },
    MARKET: {
      TICKER: '/market/ticker',
      ORDERBOOK: '/market/orderbook',
      TRADES: '/market/trades',
      CANDLES: '/market/candles',
    },
  } as const;
  
  // src/services/api/types.ts
  export interface LoginRequest {
    email: string;
    password: string;
  }
  
  export interface LoginResponse {
    token: string;
    refreshToken: string;
    user: User;
  }
  
  export interface User {
    id: string;
    email: string;
    name: string;
    role: 'user' | 'admin';
    createdAt: string;
    updatedAt: string;
  }
  
  export interface ApiKey {
    id: string;
    name: string;
    key: string;
    permissions: string[];
    createdAt: string;
    lastUsed: string | null;
  }
  
  export interface Position {
    id: string;
    symbol: string;
    side: 'long' | 'short';
    size: number;
    entryPrice: number;
    leverage: number;
    liquidationPrice: number;
    unrealizedPnl: number;
    realizedPnl: number;
    createdAt: string;
    updatedAt: string;
  }
  
  export interface Order {
    id: string;
    symbol: string;
    side: 'buy' | 'sell';
    type: 'market' | 'limit' | 'stop' | 'take_profit';
    price: number;
    size: number;
    filled: number;
    status: 'open' | 'filled' | 'canceled' | 'rejected';
    createdAt: string;
    updatedAt: string;
  }
  
  export interface Signal {
    id: string;
    botId: string;
    symbol: string;
    side: 'buy' | 'sell';
    price: number;
    timestamp: string;
    status: 'pending' | 'executed' | 'failed';
    metadata?: Record<string, any>;
  }
  
  // src/services/api/auth.service.ts
  import { apiClient } from './client';
  import { API_ENDPOINTS } from './endpoints';
  import type { LoginRequest, LoginResponse } from './types';
  
  class AuthService {
    async login(data: LoginRequest): Promise<LoginResponse> {
      try {
        const response = await apiClient.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, data);
        return response;
      } catch (error) {
        throw this.handleError(error);
      }
    }
  
    async register(data: { email: string; password: string; name: string }): Promise<void> {
      try {
        await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, data);
      } catch (error) {
        throw this.handleError(error);
      }
    }
  
    async logout(): Promise<void> {
      try {
        await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
        removeToken();
      } catch (error) {
        console.error('Logout error:', error);
        // Always remove token even if API call fails
        removeToken();
      }
    }
  
    async refreshToken(refreshToken: string): Promise<{ token: string }> {
      try {
        const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH_TOKEN, { refreshToken });
        return response;
      } catch (error) {
        throw this.handleError(error);
      }
    }
  
    private handleError(error: any): Error {
      if (error.response) {
        const message = error.response.data?.message || 'An error occurred';
        return new Error(message);
      }
      return new Error('Network error');
    }
  }
  
  export const authService = new AuthService();
  
  