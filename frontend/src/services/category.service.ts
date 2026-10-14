import { apiClient } from './api';
import { ApiResponse, Category } from '@/types';

export const categoryService = {
  async getCategories(): Promise<Category[]> {
    const res = await apiClient.get<ApiResponse<Category[]>>('/categories');
    return res.data.data;
  },

  async createCategory(payload: { name: string; slug: string; description?: string }): Promise<Category> {
    const res = await apiClient.post<ApiResponse<Category>>('/categories', payload);
    return res.data.data;
  },
};
