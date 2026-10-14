import { apiClient } from '@/services/api';
import { ApiResponse, RecommendedListingItem } from '@/types';

export interface ExtractedCriteria {
  transaction_type?: 'SALE' | 'RENT';
  category_id?: number;
  category_name?: string;
  province?: string;
  district?: string;
  budget_min?: number;
  budget_max?: number;
  area_min?: number;
  area_max?: number;
  bedrooms?: number;
  features?: string[];
}

export interface ChatMessageResponse {
  id: number;
  session_id: string;
  sender: 'USER' | 'ASSISTANT';
  message_text: string;
  created_at: string;
  listings: RecommendedListingItem[];
  suggestions: string[];
  extracted_criteria?: ExtractedCriteria;
  is_clarification: boolean;
}

export interface ChatSessionResponse {
  id: string;
  session_title: string;
  user_id?: number;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface SendMessageRequest {
  session_id?: string | null;
  message: string;
}

export const chatbotService = {
  async sendMessage(payload: SendMessageRequest): Promise<ChatMessageResponse> {
    const res = await apiClient.post<ApiResponse<ChatMessageResponse>>(
      '/chatbot/message',
      payload
    );
    return res.data.data;
  },

  async getSessions(): Promise<ChatSessionResponse[]> {
    const res = await apiClient.get<ApiResponse<ChatSessionResponse[]>>(
      '/chatbot/sessions'
    );
    return res.data.data;
  },

  async getSessionMessages(sessionId: string): Promise<ChatMessageResponse[]> {
    const res = await apiClient.get<ApiResponse<ChatMessageResponse[]>>(
      `/chatbot/sessions/${sessionId}/messages`
    );
    return res.data.data;
  },

  async deleteSession(sessionId: string): Promise<boolean> {
    const res = await apiClient.delete<ApiResponse<{ session_id: string; deleted: boolean }>>(
      `/chatbot/sessions/${sessionId}`
    );
    return res.data.success;
  },
};
