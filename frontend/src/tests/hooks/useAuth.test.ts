import { renderHook, act } from '@testing-library/react-hooks';
import { useAuth } from '@/hooks/useAuth';

describe('useAuth Hook', () => {
  it('handles login correctly', async () => {
    const { result } = renderHook(() => useAuth());
    
    await act(async () => {
      await result.current.login({
        email: 'test@example.com',
        password: 'password'
      });
    });
    
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('handles errors', async () => {
    const { result } = renderHook(() => useAuth());
    
    try {
      await act(async () => {
        await result.current.login({
          email: 'invalid',
          password: 'wrong'
        });
      });
    } catch (error) {
      expect(result.current.error).toBeTruthy();
    }
  });
});

