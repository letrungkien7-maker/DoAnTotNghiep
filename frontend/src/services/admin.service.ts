import { apiClient } from './api';
import { ApiResponse, ListingCard, PaginatedData, User } from '@/types';

export interface ModeratePayload {
  action: 'APPROVE' | 'REJECT';
  rejection_reason?: string;
}

export interface UserListParams {
  page?: number;
  size?: number;
  role?: string;
  is_active?: boolean;
  search?: string;
}

export const adminService = {
  async getPendingListings(page = 1, size = 10): Promise<PaginatedData<ListingCard>> {
    const res = await apiClient.get<ApiResponse<PaginatedData<ListingCard>>>('/admin/listings/pending', {
      params: { page, size },
    });
    return res.data.data;
  },

  async moderateListing(id: number, payload: ModeratePayload): Promise<ListingCard> {
    const res = await apiClient.patch<ApiResponse<ListingCard>>(`/admin/listings/${id}/moderate`, payload);
    return res.data.data;
  },

  async listUsers(params: UserListParams = {}): Promise<PaginatedData<User>> {
    const res = await apiClient.get<ApiResponse<PaginatedData<User>>>('/users', {
      params,
    });
    return res.data.data;
  },

  async updateUserStatus(userId: number, isActive: boolean): Promise<User> {
    const res = await apiClient.patch<ApiResponse<User>>(`/users/${userId}/status`, {
      is_active: isActive,
    });
    return res.data.data;
  },
};
