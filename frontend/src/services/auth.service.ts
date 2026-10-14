import { apiClient } from './api';
import { ApiResponse, AuthResponse, User } from '@/types';

export interface LoginParams {
  email: string;
  password: string;
}

export interface RegisterParams {
  email: string;
  password: string;
  full_name: string;
  phone_number: string;
}

export interface UpdateProfileParams {
  full_name?: string;
  phone_number?: string;
  avatar_url?: string;
}

export const authService = {
  async login(params: LoginParams): Promise<AuthResponse> {
    const res = await apiClient.post<ApiResponse<AuthResponse>>('/auth/login', params);
    const authData = res.data.data;
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('user_info', JSON.stringify(authData.user));
    return authData;
  },

  async register(params: RegisterParams): Promise<User> {
    const res = await apiClient.post<ApiResponse<User>>('/auth/register', params);
    return res.data.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout');
    } catch {
      // Ignore network error on logout
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
    }
  },

  async getProfile(): Promise<User> {
    const res = await apiClient.get<ApiResponse<User>>('/users/me');
    const user = res.data.data;
    localStorage.setItem('user_info', JSON.stringify(user));
    return user;
  },

  async updateProfile(params: UpdateProfileParams): Promise<User> {
    const res = await apiClient.put<ApiResponse<User>>('/users/me', params);
    const user = res.data.data;
    localStorage.setItem('user_info', JSON.stringify(user));
    return user;
  },

  getCurrentUser(): User | null {
    const raw = localStorage.getItem('user_info');
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  },

  getToken(): string | null {
    return localStorage.getItem('access_token');
  },
};
