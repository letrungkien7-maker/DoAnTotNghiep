import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { ListingCard } from '@/components/listings/ListingCard';
import { AuthProvider } from '@/context/AuthContext';
import { ListingCard as ListingCardType } from '@/types';

const mockListing: ListingCardType = {
  id: 1,
  title: 'Căn hộ chung cư 2PN cao cấp The Matrix One Mễ Trì',
  price: 4_200_000_000,
  price_unit: 'TOTAL',
  area: 86.5,
  bedrooms: 2,
  bathrooms: 2,
  address_text: 'Đường Lê Quang Đạo',
  province: 'Hà Nội',
  district: 'Nam Từ Liêm',
  transaction_type: 'SALE',
  category_id: 1,
  category_name: 'Căn hộ chung cư',
  thumbnail_url: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800',
  status: 'APPROVED',
  view_count: 52,
  published_at: '2026-10-12T10:00:00Z',
  created_at: '2026-10-12T09:00:00Z',
};

describe('ListingCard Component', () => {
  it('renders listing core information correctly', () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <ListingCard listing={mockListing} />
        </BrowserRouter>
      </AuthProvider>
    );

    expect(screen.getByText(mockListing.title)).toBeInTheDocument();
    expect(screen.getByText('4.2 tỷ')).toBeInTheDocument();
    expect(screen.getByText('86.5 m²')).toBeInTheDocument();
    expect(screen.getByText('2 PN')).toBeInTheDocument();
    expect(screen.getByText('2 WC')).toBeInTheDocument();
    expect(screen.getByText('Nam Từ Liêm, Hà Nội')).toBeInTheDocument();
    expect(screen.getByText('Bán')).toBeInTheDocument();
  });
});
