import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock للمتغيرات البيئية
vi.mock('@/env.ts', () => ({
  VITE_API_URL: 'http://localhost:8000/api',
  VITE_WS_URL: 'ws://localhost:8000/ws'
}));

// Mock للـ localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  clear: vi.fn()
};
global.localStorage = localStorageMock;

// Mock للـ WebSocket
class WebSocketMock {
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((data: any) => void) | null = null;
  onerror: ((error: any) => void) | null = null;
  
  constructor(url: string) {}
  
  send(data: any) {}
  close() {}
}
global.WebSocket = WebSocketMock as any;
