import axios, { AxiosError } from 'axios';
import { ApiResponse, HealthResponse } from '@/types';

let rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').trim();
if (rawBaseUrl && !rawBaseUrl.startsWith('http://') && !rawBaseUrl.startsWith('https://')) {
  rawBaseUrl = `https://${rawBaseUrl}`;
}
const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');
const API_V1_PREFIX = import.meta.env.VITE_API_V1_PREFIX || '/api/v1';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor to inject JWT token from localStorage
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle errors & session expiration
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse<unknown>>) => {
    if (error.response?.status === 401) {
      // Clear expired auth session
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      
      // Redirect to login if user was accessing a protected page
      const currentPath = window.location.pathname;
      if (
        currentPath.startsWith('/post-listing') ||
        currentPath.startsWith('/edit-listing') ||
        currentPath.startsWith('/my-listings') ||
        currentPath.startsWith('/favorites') ||
        currentPath.startsWith('/admin') ||
        currentPath.startsWith('/profile')
      ) {
        window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
      }
    }
    return Promise.reject(error);
  }
);

// Helper to extract clean error message from API response
export const getErrorMessage = (error: unknown, fallback = 'Đã có lỗi xảy ra'): string => {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as ApiResponse<unknown> | undefined;
    if (data?.error?.message) {
      return data.error.message;
    }
    if (typeof data?.message === 'string') {
      return data.message;
    }
    if (error.message === 'Network Error') {
      return 'Không thể kết nối đến máy chủ backend. Vui lòng kiểm tra lại dịch vụ.';
    }
  }
  return fallback;
};

export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};
