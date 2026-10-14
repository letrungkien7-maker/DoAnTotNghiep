import React, { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ListingCard as ListingCardType, ListingSearchParams, PaginatedData } from '@/types';
import { listingService } from '@/services/listing.service';
import { ListingFilter } from '@/components/listings/ListingFilter';
import { ListingCard } from '@/components/listings/ListingCard';
import { Pagination } from '@/components/common/Pagination';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';

export const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Extract params from URL
  const parseParamsFromUrl = useCallback((): ListingSearchParams => {
    return {
      keyword: searchParams.get('keyword') || undefined,
      category_id: searchParams.get('category_id') ? Number(searchParams.get('category_id')) : undefined,
      transaction_type: (searchParams.get('transaction_type') as ListingSearchParams['transaction_type']) || undefined,
      province: searchParams.get('province') || undefined,
      district: searchParams.get('district') || undefined,
      min_price: searchParams.get('min_price') ? Number(searchParams.get('min_price')) : undefined,
      max_price: searchParams.get('max_price') ? Number(searchParams.get('max_price')) : undefined,
      min_area: searchParams.get('min_area') ? Number(searchParams.get('min_area')) : undefined,
      max_area: searchParams.get('max_area') ? Number(searchParams.get('max_area')) : undefined,
      bedrooms: searchParams.get('bedrooms') ? Number(searchParams.get('bedrooms')) : undefined,
      sort_by: (searchParams.get('sort_by') as ListingSearchParams['sort_by']) || 'newest',
      page: searchParams.get('page') ? Number(searchParams.get('page')) : 1,
      size: 12,
    };
  }, [searchParams]);

  const [data, setData] = useState<PaginatedData<ListingCardType>>({
    items: [],
    total: 0,
    page: 1,
    size: 12,
    total_pages: 1,
  });
  const [loading, setLoading] = useState<boolean>(true);

  const currentParams = parseParamsFromUrl();

  const fetchListings = useCallback(async (params: ListingSearchParams) => {
    setLoading(true);
    try {
      const res = await listingService.searchListings(params);
      setData(res);
    } catch {
      setData({ items: [], total: 0, page: 1, size: 12, total_pages: 1 });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchListings(currentParams);
  }, [searchParams, fetchListings]);

  const handleFilterChange = (newParams: ListingSearchParams) => {
    const nextUrlParams = new URLSearchParams();
    Object.entries(newParams).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        nextUrlParams.set(k, String(v));
      }
    });
    setSearchParams(nextUrlParams);
  };

  const handlePageChange = (newPage: number) => {
    const updated = { ...currentParams, page: newPage };
    handleFilterChange(updated);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Tìm kiếm Bất động sản</h1>
        <p className="text-xs text-gray-500 mt-1">
          Lọc theo vị trí, loại hình, mức giá và diện tích phù hợp nhất với nhu cầu của bạn
        </p>
      </div>

      {/* Filter component */}
      <ListingFilter
        initialParams={currentParams}
        onFilterChange={handleFilterChange}
      />

      {/* Results header */}
      <div className="flex items-center justify-between pb-2 border-b border-gray-200">
        <p className="text-sm text-gray-600">
          Tìm thấy <strong className="text-blue-600">{data.total}</strong> bất động sản phù hợp
        </p>
      </div>

      {/* Grid or Empty */}
      {loading ? (
        <LoadingSpinner message="Đang tìm kiếm bất động sản..." />
      ) : data.items.length === 0 ? (
        <EmptyState
          title="Không tìm thấy bất động sản phù hợp"
          description="Hãy thử nới lỏng các tiêu chí lọc như khoảng giá, khu vực hoặc từ khóa để có nhiều kết quả hơn."
          actionText="Xóa tất cả bộ lọc"
          onActionClick={() => handleFilterChange({ page: 1, size: 12, sort_by: 'newest' })}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {data.items.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>

          <Pagination
            currentPage={data.page}
            totalPages={data.total_pages}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  );
};
