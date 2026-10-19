export const formatPrice = (price: number, priceUnit = 'TOTAL', transactionType = 'SALE'): string => {
  if (price <= 0) return 'Thỏa thuận';

  if (transactionType === 'RENT' || priceUnit === 'MONTH') {
    if (price >= 1_000_000) {
      const millions = price / 1_000_000;
      return `${millions % 1 === 0 ? millions : millions.toFixed(1)} triệu/tháng`;
    }
    return `${price.toLocaleString('vi-VN')} đ/tháng`;
  }

  // SALE (Mua bán)
  if (price >= 1_000_000_000) {
    const billions = price / 1_000_000_000;
    const formatted = parseFloat(billions.toFixed(2));
    return `${formatted} tỷ`;
  }
  if (price >= 1_000_000) {
    const millions = price / 1_000_000;
    const formatted = parseFloat(millions.toFixed(2));
    return `${formatted} triệu`;
  }
  return `${price.toLocaleString('vi-VN')} đ`;
};

export const formatPricePerMeter = (price: number, area: number, transactionType = 'SALE'): string => {
  if (!price || !area || price <= 0 || area <= 0) return '';
  const pricePerM2 = price / area;

  if (transactionType === 'RENT') {
    if (pricePerM2 >= 1_000_000) {
      return `~${(pricePerM2 / 1_000_000).toFixed(1)} tr/m²`;
    }
    return `~${Math.round(pricePerM2 / 1000)}k/m²`;
  }

  // SALE
  if (pricePerM2 >= 1_000_000_000) {
    return `~${(pricePerM2 / 1_000_000_000).toFixed(2)} tỷ/m²`;
  }
  if (pricePerM2 >= 1_000_000) {
    return `~${(pricePerM2 / 1_000_000).toFixed(1)} tr/m²`;
  }
  return `~${Math.round(pricePerM2).toLocaleString('vi-VN')} đ/m²`;
};

export const formatDate = (dateStr?: string | null): string => {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  } catch {
    return dateStr;
  }
};

export const getStatusBadge = (status: string): { label: string; bg: string; text: string } => {
  switch (status) {
    case 'APPROVED':
      return { label: 'Đã duyệt', bg: 'bg-green-50', text: 'text-green-700 border-green-200' };
    case 'PENDING_APPROVAL':
      return { label: 'Chờ duyệt', bg: 'bg-amber-50', text: 'text-amber-700 border-amber-200' };
    case 'REJECTED':
      return { label: 'Bị từ chối', bg: 'bg-red-50', text: 'text-red-700 border-red-200' };
    case 'DRAFT':
      return { label: 'Bản nháp', bg: 'bg-gray-100', text: 'text-gray-700 border-gray-200' };
    case 'EXPIRED':
      return { label: 'Hết hạn', bg: 'bg-purple-50', text: 'text-purple-700 border-purple-200' };
    case 'HIDDEN':
      return { label: 'Đã ẩn', bg: 'bg-slate-100', text: 'text-slate-600 border-slate-200' };
    default:
      return { label: status, bg: 'bg-gray-50', text: 'text-gray-600 border-gray-200' };
  }
};
