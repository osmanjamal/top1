import { wsService } from './websocket.service';

type MarketDataCallback = (data: any) => void;

class MarketStreamService {
  private baseUrl: string = import.meta.env.VITE_WS_URL || 'wss://api.exchange.com/ws';

  constructor() {
    this.connect();
  }

  private connect(): void {
    wsService.connect(this.baseUrl);
    
    wsService.on('error', (error) => {
      console.error('Market stream error:', error);
    });
  }

  // Subscribe to ticker updates
  subscribeTicker(symbol: string, callback: MarketDataCallback): void {
    const channel = `ticker:${symbol}`;
    wsService.subscribe(channel, callback);
  }

  unsubscribeTicker(symbol: string, callback: MarketDataCallback): void {
    const channel = `ticker:${symbol}`;
    wsService.unsubscribe(channel, callback);
  }

  // Subscribe to order book updates
  subscribeOrderBook(symbol: string, callback: MarketDataCallback): void {
    const channel = `orderbook:${symbol}`;
    wsService.subscribe(channel, callback);
  }

  unsubscribeOrderBook(symbol: string, callback: MarketDataCallback): void {
    const channel = `orderbook:${symbol}`;
    wsService.unsubscribe(channel, callback);
  }

  // Subscribe to trade updates
  subscribeTrades(symbol: string, callback: MarketDataCallback): void {
    const channel = `trades:${symbol}`;
    wsService.subscribe(channel, callback);
  }

  unsubscribeTrades(symbol: string, callback: MarketDataCallback): void {
    const channel = `trades:${symbol}`;
    wsService.unsubscribe(channel, callback);
  }

  // Subscribe to candle updates
  subscribeCandles(symbol: string, interval: string, callback: MarketDataCallback): void {
    const channel = `candles:${symbol}:${interval}`;
    wsService.subscribe(channel, callback);
  }

  unsubscribeCandles(symbol: string, interval: string, callback: MarketDataCallback): void {
    const channel = `candles:${symbol}:${interval}`;
    wsService.unsubscribe(channel, callback);
  }
}

export const marketStreamService = new MarketStreamService();

