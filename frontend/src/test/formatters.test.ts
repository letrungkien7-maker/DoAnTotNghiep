import { describe, it, expect } from 'vitest';
import { formatPrice, formatDate, getStatusBadge } from '@/utils/formatters';

describe('Formatters Utility', () => {
  it('formats sale prices correctly in billions and millions', () => {
    expect(formatPrice(3_500_000_000, 'TOTAL', 'SALE')).toBe('3.5 tỷ');
    expect(formatPrice(1_000_000_000, 'TOTAL', 'SALE')).toBe('1 tỷ');
    expect(formatPrice(850_000_000, 'TOTAL', 'SALE')).toBe('850 triệu');
    expect(formatPrice(0, 'TOTAL', 'SALE')).toBe('Thỏa thuận');
  });

  it('formats rental prices correctly per month', () => {
    expect(formatPrice(15_000_000, 'MONTH', 'RENT')).toBe('15 triệu/tháng');
    expect(formatPrice(8_500_000, 'MONTH', 'RENT')).toBe('8.5 triệu/tháng');
  });

  it('returns valid badge styles for each listing status', () => {
    expect(getStatusBadge('APPROVED').label).toBe('Đã duyệt');
    expect(getStatusBadge('PENDING_APPROVAL').label).toBe('Chờ duyệt');
    expect(getStatusBadge('REJECTED').label).toBe('Bị từ chối');
    expect(getStatusBadge('DRAFT').label).toBe('Bản nháp');
    expect(getStatusBadge('EXPIRED').label).toBe('Hết hạn');
  });

  it('formats date string cleanly', () => {
    const formatted = formatDate('2026-10-14T10:00:00Z');
    expect(formatted).toMatch(/\d{2}\/\d{2}\/\d{4}/);
  });
});
