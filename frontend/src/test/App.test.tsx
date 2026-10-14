import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock API calls so tests don't fail due to network
vi.mock('@/services/category.service', () => ({
  categoryService: {
    getCategories: vi.fn().mockResolvedValue([
      { id: 1, name: 'Căn hộ chung cư', slug: 'can-ho-chung-cu' },
      { id: 2, name: 'Nhà riêng - Nhà phố', slug: 'nha-rieng-nha-pho' },
    ]),
  },
}));

vi.mock('@/services/listing.service', () => ({
  listingService: {
    searchListings: vi.fn().mockResolvedValue({
      items: [
        {
          id: 1,
          title: 'Căn hộ mẫu 2PN Vinhomes Smart City',
          price: 3200000000,
          price_unit: 'TOTAL',
          area: 65,
          bedrooms: 2,
          bathrooms: 2,
          address_text: 'Đại lộ Thăng Long',
          province: 'Hà Nội',
          district: 'Nam Từ Liêm',
          transaction_type: 'SALE',
          category_id: 1,
          category_name: 'Căn hộ chung cư',
          thumbnail_url: null,
          status: 'APPROVED',
          view_count: 10,
          created_at: '2026-10-14T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      size: 8,
      total_pages: 1,
    }),
  },
}));

describe('Frontend App Component', () => {
  it('renders navbar branding and navigation routes', async () => {
    render(<App />);
    expect(screen.getAllByText('BDS')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Smart')[0]).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Trang chủ' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Tìm kiếm' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Mua bán' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Cho thuê' })).toBeInTheDocument();
  });

  it('renders hero title and chatbot consultation widget', async () => {
    render(<App />);
    expect(screen.getByText(/Khám phá Ngôi nhà Mơ ước/i)).toBeInTheDocument();
    expect(screen.getByText('Tư vấn AI')).toBeInTheDocument();
  });
});
