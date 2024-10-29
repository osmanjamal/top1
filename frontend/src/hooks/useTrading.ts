import { useEffect, useCallback, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useWebSocket } from './useWebSocket';
import { tradingService } from '@/services/api/trading.service';
import { marketService } from '@/services/api/market.service';
import type { 
  Order, 
  Position,
  TradingAccount,
  Balance
} from '@/types/trading';
import {
  setAccount,
  setPositions,
  setOrders,
  setLoading,
  setError
} from '@/store/slices/tradingSlice';

interface UseTradingReturn {
  account: TradingAccount | null;
  positions: Position[];
  orders: Order[];
  loading: {
    account: boolean;
    positions: boolean;
    orders: boolean;
  };
  error: string | null;
  createOrder: (orderData: any) => Promise<Order>;
  cancelOrder: (orderId: string) => Promise<void>;
  closePosition: (positionId: string) => Promise<void>;
  updateLeverage: (symbol: string, leverage: number) => Promise<void>;
  getBalances: () => Promise<Record<string, Balance>>;
  refreshData: () => Promise<void>;
}

export const useTrading = (): UseTradingReturn => {
  const dispatch = useDispatch();
  const { connected, subscribe, unsubscribe } = useWebSocket(import.meta.env.VITE_WS_URL);
  const { account, positions, orders, loading, error } = useSelector((state: any) => state.trading);

  // تحديث البيانات عند الاتصال بالـ WebSocket
  useEffect(() => {
    if (connected) {
      subscribe('account', handleAccountUpdate);
      subscribe('positions', handlePositionUpdate);
      subscribe('orders', handleOrderUpdate);
    }

    return () => {
      if (connected) {
        unsubscribe('account', handleAccountUpdate);
        unsubscribe('positions', handlePositionUpdate);
        unsubscribe('orders', handleOrderUpdate);
      }
    };
  }, [connected]);

  // معالجة تحديثات WebSocket
  const handleAccountUpdate = useCallback((data: any) => {
    dispatch(setAccount(data));
  }, []);

  const handlePositionUpdate = useCallback((data: any) => {
    dispatch(setPositions(data));
  }, []);

  const handleOrderUpdate = useCallback((data: any) => {
    dispatch(setOrders(data));
  }, []);

  // تحديث البيانات
  const refreshData = async () => {
    try {
      dispatch(setLoading({ account: true, positions: true, orders: true }));
      
      const [accountData, positionsData, ordersData] = await Promise.all([
        tradingService.getBalance(),
        tradingService.getPositions(),
        tradingService.getOrders()
      ]);

      dispatch(setAccount(accountData));
      dispatch(setPositions(positionsData));
      dispatch(setOrders(ordersData));
    } catch (error: any) {
      dispatch(setError(error.message));
    } finally {
      dispatch(setLoading({ account: false, positions: false, orders: false }));
    }
  };

  // إنشاء أمر جديد
  const createOrder = async (orderData: any) => {
    try {
      const order = await tradingService.createOrder(orderData);
      await refreshData();
      return order;
    } catch (error: any) {
      dispatch(setError(error.message));
      throw error;
    }
  };

  // إلغاء أمر
  const cancelOrder = async (orderId: string) => {
    try {
      await tradingService.cancelOrder(orderId);
      await refreshData();
    } catch (error: any) {
      dispatch(setError(error.message));
      throw error;
    }
  };

  // إغلاق مركز
  const closePosition = async (positionId: string) => {
    try {
      await tradingService.closePosition(positionId);
      await refreshData();
    } catch (error: any) {
      dispatch(setError(error.message));
      throw error;
    }
  };

  // تحديث الرافعة المالية
  const updateLeverage = async (symbol: string, leverage: number) => {
    try {
      await tradingService.updateLeverage(symbol, leverage);
      await refreshData();
    } catch (error: any) {
      dispatch(setError(error.message));
      throw error;
    }
  };

  // الحصول على الأرصدة
  const getBalances = async () => {
    try {
      const response = await tradingService.getBalance();
      dispatch(setAccount(response));
      return response.balances;
    } catch (error: any) {
      dispatch(setError(error.message));
      throw error;
    }
  };

  return {
    account,
    positions,
    orders,
    loading,
    error,
    createOrder,
    cancelOrder,
    closePosition,
    updateLeverage,
    getBalances,
    refreshData
  };
};
