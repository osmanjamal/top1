export interface User {
    id: string;
    email: string;
    name: string;
    role: 'user' | 'admin';
    status: 'active' | 'inactive' | 'blocked';
    createdAt: string;
    updatedAt: string;
  }
  
  export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    loading: boolean;
    error: string | null;
  }
  
  export interface LoginCredentials {
    email: string;
    password: string;
  }
  
  export interface RegisterData {
    name: string;
    email: string;
    password: string;
    confirmPassword: string;
  }
  
  export interface ApiKey {
    id: string;
    name: string;
    key: string;
    secret: string;
    permissions: string[];
    createdAt: string;
    lastUsed: string | null;
    status: 'active' | 'inactive';
  }
  