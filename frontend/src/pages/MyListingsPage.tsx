import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  PlusCircle,
  Eye,
  Edit3,
  Trash2,
  EyeOff,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import { ListingCard as ListingCardType } from '@/types';
import { listingService } from '@/services/listing.service';
import { formatDate, formatPrice, getStatusBadge } from '@/utils/formatters';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';

export const MyListingsPage: React.FC = () => {
  const [listings, setListings] = useState<ListingCardType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [currentTab, setCurrentTab] = useState<string>('ALL');
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

  const fetchListings = async () => {
    setLoading(true);
    try {
      const data = await listingService.getMyListings();
      setListings(data);
    } catch {
      setListings([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchListings();
  }, []);

  const handleToggleVisibility = async (id: number, currentHidden: boolean) => {
    setActionLoadingId(id);
    try {
      await listingService.toggleVisibility(id, !currentHidden);
      await fetchListings();
    } catch {
      // Ignore
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleRenew = async (id: number) => {
    if (!confirm('Bạn có chắc muốn gia hạn tin đăng này thêm 30 ngày?')) return;
    setActionLoadingId(id);
    try {
      await listingService.renewListing(id);
      await fetchListings();
    } catch {
      // Ignore
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc chắn muốn xóa vĩnh viễn tin đăng này khỏi hệ thống?')) return;
    setActionLoadingId(id);
    try {
      await listingService.deleteListing(id);
      setListings((prev) => prev.filter((item) => item.id !== id));
    } catch {
      // Ignore
    } finally {
      setActionLoadingId(null);
    }
  };

  // Filter listings by tab
  const filteredListings = listings.filter((item) => {
    if (currentTab === 'ALL') return true;
    return item.status === currentTab;
  });

  const tabs = [
    { key: 'ALL', label: 'Tất cả tin', count: listings.length },
    {
      key: 'PENDING_APPROVAL',
      label: 'Chờ duyệt',
      count: listings.filter((l) => l.status === 'PENDING_APPROVAL').length,
    },
    {
      key: 'APPROVED',
      label: 'Đã duyệt',
      count: listings.filter((l) => l.status === 'APPROVED').length,
    },
    {
      key: 'REJECTED',
      label: 'Bị từ chối',
      count: listings.filter((l) => l.status === 'REJECTED').length,
    },
    {
      key: 'DRAFT',
      label: 'Bản nháp',
      count: listings.filter((l) => l.status === 'DRAFT').length,
    },
    {
      key: 'EXPIRED',
      label: 'Hết hạn',
      count: listings.filter((l) => l.status === 'EXPIRED').length,
    },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quản lý tin đăng của tôi</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Theo dõi trạng thái kiểm duyệt, chỉnh sửa nội dung và quản lý hiển thị
          </p>
        </div>

        <Link
          to="/post-listing"
          className="inline-flex items-center space-x-1.5 px-4 py-2.5 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 shadow-xs transition text-xs shrink-0 self-start sm:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          <span>+ Đăng tin mới</span>
        </Link>
      </div>

      {/* Status Filter Tabs */}
      <div className="flex space-x-1 overflow-x-auto pb-1 border-b border-gray-200 text-xs">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setCurrentTab(tab.key)}
            className={`px-4 py-2 font-semibold rounded-t-xl transition whitespace-nowrap flex items-center space-x-1.5 border-b-2 ${
              currentTab === tab.key
                ? 'border-blue-600 text-blue-600 bg-blue-50/50'
                : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            <span>{tab.label}</span>
            <span
              className={`px-1.5 py-0.5 text-[10px] rounded-full ${
                currentTab === tab.key ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
              }`}
            >
              {tab.count}
            </span>
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSpinner message="Đang tải danh sách tin của bạn..." />
      ) : filteredListings.length === 0 ? (
        <EmptyState
          icon={<FileText className="w-10 h-10 text-gray-400" />}
          title="Không có tin đăng nào trong danh mục này"
          description="Bạn chưa có bất động sản nào ở trạng thái này."
          actionText="+ Đăng tin mới ngay"
          actionLink="/post-listing"
        />
      ) : (
        <div className="space-y-4">
          {filteredListings.map((item) => {
            const badge = getStatusBadge(item.status);
            const isPending = item.status === 'PENDING_APPROVAL';

            return (
              <div
                key={item.id}
                className="bg-white p-4 sm:p-5 rounded-2xl border border-gray-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                {/* Left info & media */}
                <div className="flex items-start space-x-4 flex-1">
                  <div className="w-28 sm:w-36 aspect-[16/10] bg-gray-100 rounded-xl overflow-hidden shrink-0 relative">
                    <img
                      src={
                        item.thumbnail_url ||
                        'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800'
                      }
                      alt={item.title}
                      className="w-full h-full object-cover"
                    />
                    <span
                      className={`absolute top-1 left-1 text-[9px] font-bold px-1.5 py-0.5 rounded text-white ${
                        item.transaction_type === 'SALE' ? 'bg-blue-600' : 'bg-emerald-600'
                      }`}
                    >
                      {item.transaction_type === 'SALE' ? 'Bán' : 'Cho thuê'}
                    </span>
                  </div>

                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`text-[11px] font-bold px-2 py-0.5 rounded-md border ${badge.bg} ${badge.text}`}
                      >
                        {badge.label}
                      </span>
                      <span className="text-xs text-blue-600 font-semibold">{item.category_name}</span>
                      <span className="text-xs text-gray-400">#{item.id}</span>
                    </div>

                    <h3 className="font-bold text-gray-900 text-sm truncate max-w-xl">
                      {item.title}
                    </h3>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                      <span className="font-bold text-blue-600 text-sm">
                        {formatPrice(item.price, item.price_unit, item.transaction_type)}
                      </span>
                      <span>•</span>
                      <span>{item.area} m²</span>
                      <span>•</span>
                      <span className="truncate max-w-[200px]">
                        {item.district ? `${item.district}, ` : ''}{item.province}
                      </span>
                      <span>•</span>
                      <span className="flex items-center space-x-1">
                        <Eye className="w-3.5 h-3.5" />
                        <span>{item.view_count} xem</span>
                      </span>
                    </div>

                    <p className="text-[11px] text-gray-400">
                      Tạo ngày: {formatDate(item.created_at)}
                      {item.published_at && ` | Xuất bản: ${formatDate(item.published_at)}`}
                    </p>
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex flex-wrap items-center gap-2 shrink-0 pt-3 md:pt-0 border-t md:border-t-0 border-gray-100 text-xs font-semibold">
                  {/* View Details */}
                  <Link
                    to={`/listings/${item.id}`}
                    className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-700 flex items-center space-x-1"
                    title="Xem trang chi tiết"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                    <span>Xem</span>
                  </Link>

                  {/* Edit: If PENDING_APPROVAL, button is still accessible to see details/warning */}
                  <Link
                    to={`/edit-listing/${item.id}`}
                    className={`p-2 border rounded-lg flex items-center space-x-1 transition ${
                      isPending
                        ? 'border-gray-200 text-gray-400 bg-gray-50'
                        : 'border-blue-200 text-blue-700 hover:bg-blue-50'
                    }`}
                    title={isPending ? 'Đang chờ duyệt (Bị khóa sửa)' : 'Chỉnh sửa tin'}
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Sửa</span>
                  </Link>

                  {/* Renew button if EXPIRED */}
                  {item.status === 'EXPIRED' && (
                    <button
                      disabled={actionLoadingId === item.id}
                      onClick={() => handleRenew(item.id)}
                      className="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center space-x-1"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      <span>Gia hạn</span>
                    </button>
                  )}

                  {/* Toggle Visibility if APPROVED or HIDDEN */}
                  {(item.status === 'APPROVED' || item.status === 'HIDDEN') && (
                    <button
                      disabled={actionLoadingId === item.id}
                      onClick={() => handleToggleVisibility(item.id, item.status === 'HIDDEN')}
                      className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-700 flex items-center space-x-1"
                      title={item.status === 'HIDDEN' ? 'Hiển thị lại' : 'Ẩn tin'}
                    >
                      {item.status === 'HIDDEN' ? (
                        <>
                          <Eye className="w-3.5 h-3.5 text-blue-600" />
                          <span>Hiện</span>
                        </>
                      ) : (
                        <>
                          <EyeOff className="w-3.5 h-3.5 text-gray-500" />
                          <span>Ẩn</span>
                        </>
                      )}
                    </button>
                  )}

                  {/* Delete */}
                  <button
                    disabled={actionLoadingId === item.id}
                    onClick={() => handleDelete(item.id)}
                    className="p-2 border border-red-200 text-red-600 rounded-lg hover:bg-red-50 flex items-center space-x-1"
                    title="Xóa tin đăng"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Xóa</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
