import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import type { LoginCredentials, RegisterData, User } from '@/types/auth';
import { authService } from '@/services/api/auth.service';
import { setUser, setToken, clearAuth, setLoading, setError } from '@/store/slices/authSlice';

interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuth = (): UseAuthReturn => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated, loading, error } = useSelector((state: any) => state.auth);

  // تحقق من حالة المصادقة عند تحميل التطبيق
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      dispatch(setLoading(true));
      const user = await authService.getProfile();
      dispatch(setUser(user));
    } catch (error) {
      dispatch(clearAuth());
    } finally {
      dispatch(setLoading(false));
    }
  };

  const login = async (credentials: LoginCredentials) => {
    try {
      dispatch(setLoading(true));
      const { token, user } = await authService.login(credentials);
      dispatch(setToken(token));
      dispatch(setUser(user));
      navigate('/dashboard');
    } catch (error: any) {
      dispatch(setError(error.message));
      throw error;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const register = async (data: RegisterData) => {
    try {
      dispatch(setLoading(true));
      await authService.register(data);
      navigate('/login');
    } catch (error: any) {
      dispatch(setError(error.message));
      throw error;
    } finally {
      dispatch(setLoading(false));
    }
  };

  const logout = async () => {
    try {
      dispatch(setLoading(true));
      await authService.logout();
      dispatch(clearAuth());
      navigate('/login');
    } catch (error: any) {
      dispatch(setError(error.message));
    } finally {
      dispatch(setLoading(false));
    }
  };

  return {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    checkAuth
  };
};

