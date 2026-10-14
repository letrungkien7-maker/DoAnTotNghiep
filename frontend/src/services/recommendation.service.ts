import { apiClient } from './api';
import { ApiResponse, RecommendedListingItem } from '@/types';

export interface RecommendationCriteria {
  transaction_type?: 'SALE' | 'RENT';
  category_id?: number;
  province?: string;
  district?: string;
  budget_min?: number;
  budget_max?: number;
  target_price?: number;
  area_min?: number;
  area_max?: number;
  target_area?: number;
  bedrooms?: number;
  features?: string[];
  top_k?: number;
}

export interface RecommendationResponse {
  items: RecommendedListingItem[];
  total: number;
  strategy: string;
  user_profile_applied: boolean;
}

export const recommendationService = {
  async searchRecommendations(criteria: RecommendationCriteria): Promise<RecommendationResponse> {
    const res = await apiClient.post<ApiResponse<RecommendationResponse>>(
      '/recommendations/search',
      criteria
    );
    return res.data.data;
  },

  async getPersonalizedFeed(limit = 8): Promise<RecommendationResponse> {
    const res = await apiClient.get<ApiResponse<RecommendationResponse>>(
      '/recommendations/personalized',
      {
        params: { limit },
      }
    );
    return res.data.data;
  },

  async getSimilarListings(listingId: number, limit = 4): Promise<RecommendationResponse> {
    const res = await apiClient.get<ApiResponse<RecommendationResponse>>(
      `/recommendations/similar/${listingId}`,
      {
        params: { limit },
      }
    );
    return res.data.data;
  },
};
