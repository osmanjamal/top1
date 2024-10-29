import { WebSocket } from 'websocket';

type WebSocketEventMap = {
  connect: void;
  disconnect: void;
  error: Error;
  message: any;
};

type WebSocketEventHandler<K extends keyof WebSocketEventMap> = (
  event: WebSocketEventMap[K]
) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private subscribers: Map<string, Set<(data: any) => void>> = new Map();
  private eventHandlers: Partial<Record<keyof WebSocketEventMap, Set<WebSocketEventHandler<any>>>> = {};

  connect(url: string): void {
    try {
      this.ws = new WebSocket(url);
      this.setupEventListeners();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.handleReconnect();
    }
  }

  private setupEventListeners(): void {
    if (!this.ws) return;

    this.ws.on('open', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.emit('connect');
    });

    this.ws.on('close', () => {
      console.log('WebSocket disconnected');
      this.emit('disconnect');
      this.handleReconnect();
    });

    this.ws.on('error', (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    });

    this.ws.on('message', (data) => {
      try {
        const parsedData = JSON.parse(data.toString());
        this.handleMessage(parsedData);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      setTimeout(() => {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect(this.ws?.url || '');
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
      this.emit('error', new Error('WebSocket connection failed'));
    }
  }

  subscribe(channel: string, callback: (data: any) => void): void {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, new Set());
    }
    this.subscribers.get(channel)?.add(callback);

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.send({
        action: 'subscribe',
        channel: channel
      });
    }
  }

  unsubscribe(channel: string, callback: (data: any) => void): void {
    this.subscribers.get(channel)?.delete(callback);
    if (this.subscribers.get(channel)?.size === 0) {
      this.subscribers.delete(channel);
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          action: 'unsubscribe',
          channel: channel
        });
      }
    }
  }

  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  private handleMessage(message: any): void {
    const { channel, data } = message;
    if (channel && this.subscribers.has(channel)) {
      this.subscribers.get(channel)?.forEach(callback => callback(data));
    }
    this.emit('message', message);
  }

  on<K extends keyof WebSocketEventMap>(
    event: K,
    handler: WebSocketEventHandler<K>
  ): void {
    if (!this.eventHandlers[event]) {
      this.eventHandlers[event] = new Set();
    }
    this.eventHandlers[event]?.add(handler);
  }

  off<K extends keyof WebSocketEventMap>(
    event: K,
    handler: WebSocketEventHandler<K>
  ): void {
    this.eventHandlers[event]?.delete(handler);
  }

  private emit<K extends keyof WebSocketEventMap>(
    event: K,
    data?: WebSocketEventMap[K]
  ): void {
    this.eventHandlers[event]?.forEach(handler => handler(data));
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsService = new WebSocketService();
