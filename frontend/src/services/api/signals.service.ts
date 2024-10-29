import type { Signal } from './types';

interface SignalStats {
  total: number;
  successful: number;
  failed: number;
  pending: number;
  successRate: number;
  averageProfit: number;
  timeStats: {
    avgExecutionTime: number;
    avgSuccessTime: number;
  };
}

interface CreateSignalRequest {
  botId: string;
  symbol: string;
  side: 'buy' | 'sell';
  price: number;
  size?: number;
  metadata?: Record<string, any>;
}

class SignalsService {
  async getSignals(params?: {
    botId?: string;
    status?: 'pending' | 'executed' | 'failed';
    from?: string;
    to?: string;
    limit?: number;
  }): Promise<Signal[]> {
    try {
      const response = await apiClient.get<Signal[]>(API_ENDPOINTS.SIGNALS.LIST, { params });
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createSignal(data: CreateSignalRequest): Promise<Signal> {
    try {
      const response = await apiClient.post<Signal>(API_ENDPOINTS.SIGNALS.CREATE, data);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateSignal(signalId: string, data: Partial<Signal>): Promise<Signal> {
    try {
      const response = await apiClient.put<Signal>(
        `${API_ENDPOINTS.SIGNALS.UPDATE}/${signalId}`,
        data
      );
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteSignal(signalId: string): Promise<void> {
    try {
      await apiClient.delete(`${API_ENDPOINTS.SIGNALS.DELETE}/${signalId}`);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getStats(params?: {
    botId?: string;
    from?: string;
    to?: string;
  }): Promise<SignalStats> {
    try {
      const response = await apiClient.get<SignalStats>(API_ENDPOINTS.SIGNALS.STATS, { params });
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (error.response) {
      const message = error.response.data?.message || 'Signal operation failed';
      return new Error(message);
    }
    return new Error('Network error');
  }
}

export const signalsService = new SignalsService();
