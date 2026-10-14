import { apiClient } from './api';
import {
  ApiResponse,
  ListingCard,
  ListingCreatePayload,
  ListingDetail,
  ListingSearchParams,
  PaginatedData,
} from '@/types';

export const listingService = {
  async searchListings(params: ListingSearchParams = {}): Promise<PaginatedData<ListingCard>> {
    const res = await apiClient.get<ApiResponse<PaginatedData<ListingCard>>>('/listings', {
      params,
    });
    return res.data.data;
  },

  async getListingDetail(id: number): Promise<ListingDetail> {
    const res = await apiClient.get<ApiResponse<ListingDetail>>(`/listings/${id}`);
    return res.data.data;
  },

  async createListing(payload: ListingCreatePayload): Promise<ListingDetail> {
    const res = await apiClient.post<ApiResponse<ListingDetail>>('/listings', payload);
    return res.data.data;
  },

  async updateListing(
    id: number,
    payload: Partial<ListingCreatePayload> & { submit_for_approval?: boolean }
  ): Promise<ListingDetail> {
    const res = await apiClient.put<ApiResponse<ListingDetail>>(`/listings/${id}`, payload);
    return res.data.data;
  },

  async deleteListing(id: number): Promise<void> {
    await apiClient.delete(`/listings/${id}`);
  },

  async getMyListings(): Promise<ListingCard[]> {
    const res = await apiClient.get<ApiResponse<ListingCard[]>>('/listings/my/all');
    return res.data.data;
  },

  async toggleVisibility(id: number, isHidden: boolean): Promise<void> {
    await apiClient.patch(`/listings/${id}/visibility`, { is_hidden: isHidden });
  },

  async renewListing(id: number): Promise<void> {
    await apiClient.post(`/listings/${id}/renew`);
  },
};
