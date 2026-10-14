import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock the API checkHealth to avoid network dependency in unit test
vi.mock('@/services/api', () => ({
  checkHealth: vi.fn().mockResolvedValue({
    status: 'healthy',
    app_name: 'Real Estate Business API',
    environment: 'development',
    version: '1.0.0',
    database: {
      status: 'connected',
      dialect: 'postgresql',
      latency_ms: 12.5,
      error: null,
    },
    timestamp: '2026-10-14T13:00:00Z',
  }),
}));

describe('Frontend App Component', () => {
  it('renders application branding and header elements', async () => {
    render(<App />);
    expect(screen.getByText('BDS SmartPlatform')).toBeInTheDocument();
    expect(screen.getByText('Hệ Thống Bất Động Sản Thông Minh')).toBeInTheDocument();
  });

  it('renders health check container and architectural pillars', async () => {
    render(<App />);
    expect(await screen.findByText(/Tình trạng Hệ thống/i)).toBeInTheDocument();
    expect(screen.getByText('Sàn Giao Dịch BĐS')).toBeInTheDocument();
    expect(screen.getByText('Trợ Lý Ảo Chatbot AI')).toBeInTheDocument();
    expect(screen.getByText('Gợi Ý Thông Minh')).toBeInTheDocument();
  });
});
