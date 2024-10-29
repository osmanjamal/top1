import type { User, ApiKey } from './types';

class UserService {
  async getProfile(): Promise<User> {
    try {
      const response = await apiClient.get<User>(API_ENDPOINTS.USER.PROFILE);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    try {
      const response = await apiClient.put<User>(API_ENDPOINTS.USER.UPDATE_PROFILE, data);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async changePassword(data: { currentPassword: string; newPassword: string }): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.USER.CHANGE_PASSWORD, data);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getApiKeys(): Promise<ApiKey[]> {
    try {
      const response = await apiClient.get<ApiKey[]>(API_ENDPOINTS.USER.API_KEYS);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createApiKey(data: { name: string; permissions: string[] }): Promise<ApiKey> {
    try {
      const response = await apiClient.post<ApiKey>(API_ENDPOINTS.USER.API_KEYS, data);
      return response;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteApiKey(id: string): Promise<void> {
    try {
      await apiClient.delete(`${API_ENDPOINTS.USER.API_KEYS}/${id}`);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (error.response) {
      const message = error.response.data?.message || 'An error occurred';
      return new Error(message);
    }
    return new Error('Network error');
  }
}

export const userService = new UserService();
