import { authService } from '@/services/api/auth.service';
import { vi } from 'vitest';

describe('Auth Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('successfully logs in user', async () => {
    const mockResponse = {
      token: 'test-token',
      user: {
        id: '1',
        email: 'test@example.com',
        name: 'Test User'
      }
    };

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });

    const result = await authService.login({
      email: 'test@example.com',
      password: 'password'
    });

    expect(result).toEqual(mockResponse);
  });

  it('handles login errors', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Invalid credentials'));

    await expect(authService.login({
      email: 'test@example.com',
      password: 'wrong'
    })).rejects.toThrow('Invalid credentials');
  });
});
