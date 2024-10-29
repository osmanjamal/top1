interface MetricDataPoint {
    timestamp: number;
    value: number;
    metadata?: Record<string, any>;
  }
  
  interface PerformanceMetrics {
    winRate: number;
    profitFactor: number;
    averageWin: number;
    averageLoss: number;
    maxDrawdown: number;
    sharpeRatio: number;
    trades: number;
  }
  
  class MetricsService {
    private metrics: Map<string, MetricDataPoint[]> = new Map();
  
    // Record a new metric data point
    record(metricName: string, value: number, metadata?: Record<string, any>): void {
      if (!this.metrics.has(metricName)) {
        this.metrics.set(metricName, []);
      }
  
      const dataPoint: MetricDataPoint = {
        timestamp: Date.now(),
        value,
        metadata
      };
  
      this.metrics.get(metricName)?.push(dataPoint);
    }
  
    // Get metric data points for a specific time range
    getMetrics(metricName: string, params?: {
      from?: number;
      to?: number;
      limit?: number;
    }): MetricDataPoint[] {
      const metricData = this.metrics.get(metricName) || [];
      let filteredData = metricData;
  
      if (params?.from) {
        filteredData = filteredData.filter(point => point.timestamp >= params.from!);
      }
  
      if (params?.to) {
        filteredData = filteredData.filter(point => point.timestamp <= params.to!);
      }
  
      if (params?.limit) {
        filteredData = filteredData.slice(-params.limit);
      }
  
      return filteredData;
    }
  
    // Calculate performance metrics
    calculatePerformanceMetrics(trades: any[]): PerformanceMetrics {
      const winningTrades = trades.filter(trade => trade.pnl > 0);
      const losingTrades = trades.filter(trade => trade.pnl < 0);
  
      const winRate = (winningTrades.length / trades.length) * 100;
      const averageWin = winningTrades.reduce((sum, trade) => sum + trade.pnl, 0) / winningTrades.length;
      const averageLoss = Math.abs(losingTrades.reduce((sum, trade) => sum + trade.pnl, 0) / losingTrades.length);
      const profitFactor = averageWin / averageLoss;
  
      // Calculate max drawdown
      let maxDrawdown = 0;
      let peak = -Infinity;
      let balance = 0;
  
      trades.forEach(trade => {
        balance += trade.pnl;
        if (balance > peak) {
          peak = balance;
        }
        const drawdown = (peak - balance) / peak * 100;
        if (drawdown > maxDrawdown) {
          maxDrawdown = drawdown;
        }
      });
  
      // Calculate Sharpe Ratio (simplified)
      const returns = trades.map(trade => trade.pnl);
      const averageReturn = returns.reduce((sum, ret) => sum + ret, 0) / returns.length;
      const stdDev = Math.sqrt(
        returns.reduce((sum, ret) => sum + Math.pow(ret - averageReturn, 2), 0) / returns.length
      );
      const sharpeRatio = (averageReturn / stdDev) * Math.sqrt(252); // Annualized
  
      return {
        winRate,
        profitFactor,
        averageWin,
        averageLoss,
        maxDrawdown,
        sharpeRatio,
        trades: trades.length
      };
    }
  
    // Clear old metrics data
    clearOldMetrics(olderThan: number): void {
      const now = Date.now();
      for (const [metricName, dataPoints] of this.metrics.entries()) {
        const filteredPoints = dataPoints.filter(point => now - point.timestamp <= olderThan);
        this.metrics.set(metricName, filteredPoints);
      }
    }
  }
  
  export const metricsService = new MetricsService();
  