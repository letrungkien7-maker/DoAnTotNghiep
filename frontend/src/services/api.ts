import axios from 'axios';
import { HealthResponse } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const API_V1_PREFIX = import.meta.env.VITE_API_V1_PREFIX || '/api/v1';

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export const checkHealth = async (): Promise<HealthResponse> => {
  // Fetch from /api/v1/health or fallback to /health
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};
