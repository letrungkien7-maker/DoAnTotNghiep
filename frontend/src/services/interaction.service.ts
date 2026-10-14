import { apiClient } from './api';
import { ApiResponse, Inquiry, InquiryCreatePayload, ListingCard } from '@/types';

export interface FavoriteToggleResult {
  listing_id: number;
  is_favorited: boolean;
  message: string;
}

export const interactionService = {
  async toggleFavorite(listingId: number): Promise<FavoriteToggleResult> {
    const res = await apiClient.post<ApiResponse<FavoriteToggleResult>>(`/favorites/${listingId}`);
    return res.data.data;
  },

  async getFavorites(): Promise<ListingCard[]> {
    const res = await apiClient.get<ApiResponse<ListingCard[]>>('/favorites');
    return res.data.data;
  },

  async sendInquiry(payload: InquiryCreatePayload): Promise<Inquiry> {
    const res = await apiClient.post<ApiResponse<Inquiry>>('/inquiries', payload);
    return res.data.data;
  },

  async getReceivedInquiries(): Promise<Inquiry[]> {
    const res = await apiClient.get<ApiResponse<Inquiry[]>>('/inquiries/received');
    return res.data.data;
  },

  async updateInquiryStatus(id: number, status: 'CONTACTED' | 'CLOSED'): Promise<Inquiry> {
    const res = await apiClient.patch<ApiResponse<Inquiry>>(`/inquiries/${id}/status`, { status });
    return res.data.data;
  },
};
