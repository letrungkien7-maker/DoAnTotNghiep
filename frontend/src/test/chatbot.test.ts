import { describe, it, expect, vi } from 'vitest';
import { chatbotService } from '@/services/chatbot.service';
import { apiClient } from '@/services/api';

vi.mock('@/services/api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Chatbot Service', () => {
  it('sends message to chatbot endpoint and returns response data', async () => {
    const mockResponseData = {
      id: 101,
      session_id: 'session-uuid-123',
      sender: 'ASSISTANT',
      message_text: 'Dưới đây là 3 căn hộ phù hợp tại Nam Từ Liêm',
      created_at: new Date().toISOString(),
      listings: [
        {
          id: 1,
          title: 'Vinhomes Smart City 2PN',
          price: 3200000000,
          area: 65,
          district: 'Nam Từ Liêm',
          province: 'Hà Nội',
          match_percentage: 95,
          match_reasons: ['Giá trong tầm ngân sách', 'Đúng khu vực'],
        },
      ],
      suggestions: ['Xem thêm căn hộ', 'Đổi sang Cầu Giấy'],
      extracted_criteria: {
        province: 'Hà Nội',
        district: 'Nam Từ Liêm',
        budget_max: 3500000000,
      },
      is_clarification: false,
    };

    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: {
        success: true,
        data: mockResponseData,
        message: 'Success',
      },
    });

    const result = await chatbotService.sendMessage({
      session_id: 'session-uuid-123',
      message: 'Tìm căn hộ 2pn Nam Từ Liêm dưới 3.5 tỷ',
    });

    expect(apiClient.post).toHaveBeenCalledWith('/chatbot/message', {
      session_id: 'session-uuid-123',
      message: 'Tìm căn hộ 2pn Nam Từ Liêm dưới 3.5 tỷ',
    });
    expect(result.session_id).toBe('session-uuid-123');
    expect(result.listings).toHaveLength(1);
    expect(result.listings[0].title).toBe('Vinhomes Smart City 2PN');
  });

  it('fetches chat sessions list', async () => {
    const mockSessions = [
      {
        id: 'sess-1',
        session_title: 'Tìm căn hộ 2PN',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 4,
      },
    ];

    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        success: true,
        data: mockSessions,
        message: 'Success',
      },
    });

    const sessions = await chatbotService.getSessions();
    expect(apiClient.get).toHaveBeenCalledWith('/chatbot/sessions');
    expect(sessions).toHaveLength(1);
    expect(sessions[0].id).toBe('sess-1');
  });

  it('deletes a chat session by id', async () => {
    vi.mocked(apiClient.delete).mockResolvedValueOnce({
      data: {
        success: true,
        data: { session_id: 'sess-1', deleted: true },
        message: 'Deleted',
      },
    });

    const deleted = await chatbotService.deleteSession('sess-1');
    expect(apiClient.delete).toHaveBeenCalledWith('/chatbot/sessions/sess-1');
    expect(deleted).toBe(true);
  });
});
