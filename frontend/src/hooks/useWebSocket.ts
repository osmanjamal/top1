import { useEffect, useRef, useCallback, useState } from 'react';
import { wsService } from '@/services/websocket/websocket.service';

interface WebSocketHookOptions {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Error) => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface UseWebSocketReturn {
  connected: boolean;
  subscribe: (channel: string, callback: (data: any) => void) => void;
  unsubscribe: (channel: string, callback: (data: any) => void) => void;
  send: (data: any) => void;
  error: Error | null;
}

export const useWebSocket = (url: string, options: WebSocketHookOptions = {}): UseWebSocketReturn => {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const subscriptionsRef = useRef(new Map<string, Set<(data: any) => void>>());

  const handleConnect = useCallback(() => {
    setConnected(true);
    setError(null);
    options.onConnect?.();
  }, [options]);

  const handleDisconnect = useCallback(() => {
    setConnected(false);
    options.onDisconnect?.();
  }, [options]);

  const handleError = useCallback((err: Error) => {
    setError(err);
    options.onError?.(err);
  }, [options]);

  useEffect(() => {
    wsService.on('connect', handleConnect);
    wsService.on('disconnect', handleDisconnect);
    wsService.on('error', handleError);

    wsService.connect(url);

    return () => {
      wsService.disconnect();
    };
  }, [url, handleConnect, handleDisconnect, handleError]);

  const subscribe = useCallback((channel: string, callback: (data: any) => void) => {
    if (!subscriptionsRef.current.has(channel)) {
      subscriptionsRef.current.set(channel, new Set());
    }
    subscriptionsRef.current.get(channel)?.add(callback);
    wsService.subscribe(channel, callback);
  }, []);

  const unsubscribe = useCallback((channel: string, callback: (data: any) => void) => {
    const callbacks = subscriptionsRef.current.get(channel);
    if (callbacks) {
      callbacks.delete(callback);
      wsService.unsubscribe(channel, callback);
      if (callbacks.size === 0) {
        subscriptionsRef.current.delete(channel);
      }
    }
  }, []);

  const send = useCallback((data: any) => {
    wsService.send(data);
  }, []);

  return { connected, subscribe, unsubscribe, send, error };
};
