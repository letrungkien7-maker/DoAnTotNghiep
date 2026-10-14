import React, { useEffect, useState } from 'react';
import { Search, RotateCcw, Filter } from 'lucide-react';
import { Category, ListingSearchParams, TransactionType } from '@/types';
import { categoryService } from '@/services/category.service';

interface ListingFilterProps {
  initialParams: ListingSearchParams;
  onFilterChange: (params: ListingSearchParams) => void;
  compact?: boolean;
}

export const ListingFilter: React.FC<ListingFilterProps> = ({
  initialParams,
  onFilterChange,
  compact = false,
}) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [params, setParams] = useState<ListingSearchParams>(initialParams);
  const [isExpanded, setIsExpanded] = useState(!compact);

  useEffect(() => {
    categoryService.getCategories().then(setCategories).catch(() => {});
  }, []);

  const handleChange = (key: keyof ListingSearchParams, value: unknown) => {
    const updated = { ...params, [key]: value };
    // Clear undefined/empty strings
    if (value === '' || value === undefined || value === null) {
      delete updated[key];
    }
    setParams(updated);
  };

  const handleApply = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    onFilterChange({ ...params, page: 1 });
  };

  const handleReset = () => {
    const resetParams: ListingSearchParams = {
      page: 1,
      size: initialParams.size || 12,
      sort_by: 'newest',
    };
    setParams(resetParams);
    onFilterChange(resetParams);
  };

  const PROVINCES = [
    'Hà Nội',
    'Hồ Chí Minh',
    'Đà Nẵng',
    'Hải Phòng',
    'Bình Dương',
    'Đồng Nai',
    'Cần Thơ',
    'Khánh Hòa',
  ];

  return (
    <form onSubmit={handleApply} className="bg-white p-5 rounded-xl border border-gray-200 shadow-xs mb-6">
      {/* Top Search bar */}
      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={params.keyword || ''}
            onChange={(e) => handleChange('keyword', e.target.value)}
            placeholder="Tìm theo địa điểm, dự án, tên đường, từ khóa..."
            className="w-full pl-10 pr-4 py-2.5 text-sm bg-gray-50 border border-gray-300 rounded-lg focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Transaction Type Buttons */}
        <div className="inline-flex rounded-lg border border-gray-200 p-1 bg-gray-50 shrink-0">
          <button
            type="button"
            onClick={() => handleChange('transaction_type', undefined)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition ${
              !params.transaction_type ? 'bg-white shadow-2xs text-blue-600' : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Tất cả
          </button>
          <button
            type="button"
            onClick={() => handleChange('transaction_type', 'SALE' as TransactionType)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition ${
              params.transaction_type === 'SALE'
                ? 'bg-blue-600 text-white shadow-2xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Mua bán
          </button>
          <button
            type="button"
            onClick={() => handleChange('transaction_type', 'RENT' as TransactionType)}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition ${
              params.transaction_type === 'RENT'
                ? 'bg-emerald-600 text-white shadow-2xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Cho thuê
          </button>
        </div>

        <button
          type="submit"
          className="px-5 py-2.5 bg-blue-600 text-white font-medium text-sm rounded-lg hover:bg-blue-700 transition flex items-center justify-center space-x-2 shrink-0 shadow-xs"
        >
          <Search className="w-4 h-4" />
          <span>Tìm kiếm</span>
        </button>

        {compact && (
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-700 flex items-center justify-center space-x-1 hover:bg-gray-50"
          >
            <Filter className="w-4 h-4 text-gray-500" />
            <span>Bộ lọc</span>
          </button>
        )}
      </div>

      {/* Advanced Filter grid */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          {/* Category */}
          <div>
            <label className="block text-gray-700 font-semibold mb-1">Loại hình BĐS</label>
            <select
              value={params.category_id || ''}
              onChange={(e) => handleChange('category_id', e.target.value ? Number(e.target.value) : undefined)}
              className="w-full p-2 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Tất cả loại hình</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Location */}
          <div>
            <label className="block text-gray-700 font-semibold mb-1">Tỉnh / Thành phố</label>
            <select
              value={params.province || ''}
              onChange={(e) => handleChange('province', e.target.value || undefined)}
              className="w-full p-2 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Toàn quốc</option>
              {PROVINCES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>

          {/* Price Range Preset */}
          <div>
            <label className="block text-gray-700 font-semibold mb-1">Mức giá</label>
            <select
              value={
                params.min_price || params.max_price
                  ? `${params.min_price || 0}-${params.max_price || 0}`
                  : ''
              }
              onChange={(e) => {
                const val = e.target.value;
                if (!val) {
                  handleChange('min_price', undefined);
                  handleChange('max_price', undefined);
                } else {
                  const [min, max] = val.split('-').map(Number);
                  handleChange('min_price', min > 0 ? min : undefined);
                  handleChange('max_price', max > 0 ? max : undefined);
                }
              }}
              className="w-full p-2 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Tất cả mức giá</option>
              <option value="0-2000000000">Dưới 2 tỷ</option>
              <option value="2000000000-4000000000">2 - 4 tỷ</option>
              <option value="4000000000-7000000000">4 - 7 tỷ</option>
              <option value="7000000000-12000000000">7 - 12 tỷ</option>
              <option value="12000000000-0">Trên 12 tỷ</option>
            </select>
          </div>

          {/* Area Range Preset */}
          <div>
            <label className="block text-gray-700 font-semibold mb-1">Diện tích (m²)</label>
            <select
              value={
                params.min_area || params.max_area
                  ? `${params.min_area || 0}-${params.max_area || 0}`
                  : ''
              }
              onChange={(e) => {
                const val = e.target.value;
                if (!val) {
                  handleChange('min_area', undefined);
                  handleChange('max_area', undefined);
                } else {
                  const [min, max] = val.split('-').map(Number);
                  handleChange('min_area', min > 0 ? min : undefined);
                  handleChange('max_area', max > 0 ? max : undefined);
                }
              }}
              className="w-full p-2 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Tất cả diện tích</option>
              <option value="0-50">Dưới 50 m²</option>
              <option value="50-80">50 - 80 m²</option>
              <option value="80-120">80 - 120 m²</option>
              <option value="120-200">120 - 200 m²</option>
              <option value="200-0">Trên 200 m²</option>
            </select>
          </div>

          {/* Bedrooms */}
          <div>
            <label className="block text-gray-700 font-semibold mb-1">Số phòng ngủ</label>
            <select
              value={params.bedrooms || ''}
              onChange={(e) => handleChange('bedrooms', e.target.value ? Number(e.target.value) : undefined)}
              className="w-full p-2 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">Bất kỳ</option>
              <option value="1">1+ phòng ngủ</option>
              <option value="2">2+ phòng ngủ</option>
              <option value="3">3+ phòng ngủ</option>
              <option value="4">4+ phòng ngủ</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label className="block text-gray-700 font-semibold mb-1">Sắp xếp theo</label>
            <select
              value={params.sort_by || 'newest'}
              onChange={(e) => handleChange('sort_by', e.target.value as ListingSearchParams['sort_by'])}
              className="w-full p-2 bg-gray-50 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="newest">Mới nhất</option>
              <option value="price_asc">Giá: Thấp đến cao</option>
              <option value="price_desc">Giá: Cao đến thấp</option>
              <option value="area_asc">Diện tích: Nhỏ đến lớn</option>
              <option value="area_desc">Diện tích: Lớn đến nhỏ</option>
            </select>
          </div>

          {/* Reset button */}
          <div className="sm:col-span-2 flex items-end justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={handleReset}
              className="px-3 py-2 text-xs font-medium text-gray-600 hover:text-gray-900 border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center space-x-1"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Xóa bộ lọc</span>
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition"
            >
              Áp dụng lọc
            </button>
          </div>
        </div>
      )}
    </form>
  );
};
