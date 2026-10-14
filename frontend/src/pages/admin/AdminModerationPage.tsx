import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Check,
  X,
  AlertCircle,
  Eye,
  Loader2,
  CheckCircle2,
} from 'lucide-react';
import { ListingCard as ListingCardType, ListingDetail, PaginatedData } from '@/types';
import { adminService } from '@/services/admin.service';
import { listingService } from '@/services/listing.service';
import { formatDate, formatPrice } from '@/utils/formatters';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';
import { Pagination } from '@/components/common/Pagination';
import { getErrorMessage } from '@/services/api';

export const AdminModerationPage: React.FC = () => {
  const [data, setData] = useState<PaginatedData<ListingCardType>>({
    items: [],
    total: 0,
    page: 1,
    size: 10,
    total_pages: 1,
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedListing, setSelectedListing] = useState<ListingDetail | null>(null);
  const [, setLoadingDetail] = useState<boolean>(false);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [rejectMode, setRejectMode] = useState<boolean>(false);
  const [rejectionReason, setRejectionReason] = useState<string>('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(
    null
  );

  const fetchPending = async (page = 1) => {
    setLoading(true);
    try {
      const res = await adminService.getPendingListings(page, 10);
      setData(res);
    } catch {
      setData({ items: [], total: 0, page: 1, size: 10, total_pages: 1 });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  const handleOpenReview = async (id: number) => {
    setLoadingDetail(true);
    setRejectMode(false);
    setRejectionReason('');
    setFeedback(null);
    try {
      const detail = await listingService.getListingDetail(id);
      setSelectedListing(detail);
    } catch (err) {
      alert(getErrorMessage(err, 'Không thể tải chi tiết tin để duyệt'));
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedListing) return;
    setActionLoading(true);
    setFeedback(null);
    try {
      await adminService.moderateListing(selectedListing.id, { action: 'APPROVE' });
      setFeedback({ type: 'success', message: 'Phê duyệt tin thành công! Tin đã được xuất bản.' });
      setTimeout(() => {
        setSelectedListing(null);
        fetchPending(data.page);
      }, 1500);
    } catch (err) {
      setFeedback({ type: 'error', message: getErrorMessage(err, 'Lỗi khi duyệt tin') });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedListing) return;
    if (!rejectionReason.trim() || rejectionReason.trim().length < 5) {
      setFeedback({
        type: 'error',
        message: 'Vui lòng nhập lý do từ chối cụ thể (tối thiểu 5 ký tự)',
      });
      return;
    }

    setActionLoading(true);
    setFeedback(null);
    try {
      await adminService.moderateListing(selectedListing.id, {
        action: 'REJECT',
        rejection_reason: rejectionReason.trim(),
      });
      setFeedback({
        type: 'success',
        message: 'Đã từ chối tin đăng và gửi phản hồi lý do cho chủ tin.',
      });
      setTimeout(() => {
        setSelectedListing(null);
        fetchPending(data.page);
      }, 1500);
    } catch (err) {
      setFeedback({ type: 'error', message: getErrorMessage(err, 'Lỗi khi từ chối tin') });
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
            <ShieldCheck className="w-6 h-6 text-amber-600" />
            <span>Hàng đợi kiểm duyệt bất động sản</span>
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            Tổng cộng: <strong className="text-amber-600">{data.total}</strong> tin đang chờ xử lý
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Đang tải danh sách tin chờ duyệt..." />
      ) : data.items.length === 0 ? (
        <EmptyState
          icon={<CheckCircle2 className="w-10 h-10 text-green-500" />}
          title="Không có tin đăng nào chờ duyệt"
          description="Hiện tại hàng đợi đang trống. Toàn bộ tin đăng đã được xử lý xong!"
        />
      ) : (
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-600">
              <thead className="bg-gray-50 border-b border-gray-200 text-gray-700 font-bold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3 px-4">Ảnh & Tiêu đề</th>
                  <th className="py-3 px-4">Loại hình</th>
                  <th className="py-3 px-4">Mức giá</th>
                  <th className="py-3 px-4">Địa điểm</th>
                  <th className="py-3 px-4">Ngày nộp</th>
                  <th className="py-3 px-4 text-center">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.items.map((item) => (
                  <tr key={item.id} className="hover:bg-blue-50/40 transition">
                    <td className="py-3 px-4 flex items-center space-x-3">
                      <img
                        src={
                          item.thumbnail_url ||
                          'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800'
                        }
                        alt="thumb"
                        className="w-14 h-10 rounded-lg object-cover shrink-0"
                      />
                      <div className="min-w-0">
                        <span className="font-bold text-gray-900 block truncate max-w-xs">
                          {item.title}
                        </span>
                        <span className="text-[10px] text-gray-400">ID: #{item.id}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 font-semibold text-gray-700">{item.category_name}</td>
                    <td className="py-3 px-4 font-bold text-blue-600">
                      {formatPrice(item.price, item.price_unit, item.transaction_type)}
                    </td>
                    <td className="py-3 px-4 truncate max-w-[150px]">{item.province}</td>
                    <td className="py-3 px-4 text-gray-400">{formatDate(item.created_at)}</td>
                    <td className="py-3 px-4 text-center">
                      <button
                        onClick={() => handleOpenReview(item.id)}
                        className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold shadow-2xs transition inline-flex items-center space-x-1"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Xem & Duyệt</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={data.page}
            totalPages={data.total_pages}
            onPageChange={(page) => fetchPending(page)}
          />
        </div>
      )}

      {/* Review & Moderation Modal */}
      {selectedListing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-2xs animate-in fade-in duration-150">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden border border-gray-100">
            {/* Header */}
            <div className="p-4 bg-slate-900 text-white flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold text-base">Kiểm duyệt tin đăng #{selectedListing.id}</h3>
              </div>
              <button
                onClick={() => setSelectedListing(null)}
                className="p-1 text-slate-400 hover:text-white rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Scrollable details body */}
            <div className="p-6 overflow-y-auto space-y-5 text-xs">
              {feedback && (
                <div
                  className={`p-3 rounded-xl flex items-start space-x-2 ${
                    feedback.type === 'success'
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-700 border border-red-200'
                  }`}
                >
                  {feedback.type === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  )}
                  <span className="font-semibold">{feedback.message}</span>
                </div>
              )}

              {/* Image Preview Grid */}
              <div>
                <label className="font-bold text-gray-700 block mb-2">
                  Bộ sưu tập hình ảnh ({selectedListing.images.length} ảnh):
                </label>
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                  {selectedListing.images.map((img, i) => (
                    <a
                      key={i}
                      href={img.image_url}
                      target="_blank"
                      rel="noreferrer"
                      className="aspect-[4/3] rounded-lg overflow-hidden border border-gray-200 hover:opacity-90 block relative group"
                    >
                      <img src={img.image_url} alt="" className="w-full h-full object-cover" />
                      {img.is_thumbnail && (
                        <span className="absolute bottom-1 left-1 px-1 py-0.5 bg-blue-600 text-white text-[8px] font-bold rounded">
                          Ảnh đại diện
                        </span>
                      )}
                    </a>
                  ))}
                </div>
              </div>

              {/* Title & Core Details */}
              <div className="space-y-2">
                <h4 className="text-base font-bold text-gray-900">{selectedListing.title}</h4>
                <div className="flex flex-wrap gap-3 font-semibold">
                  <span className="text-blue-600 text-sm">
                    {formatPrice(selectedListing.price, selectedListing.price_unit, selectedListing.transaction_type)}
                  </span>
                  <span>• {selectedListing.area} m²</span>
                  <span>• {selectedListing.category_name}</span>
                  <span>• {selectedListing.address_text}, {selectedListing.province}</span>
                </div>
              </div>

              {/* Description */}
              <div className="p-4 bg-gray-50 rounded-xl space-y-1">
                <span className="font-bold text-gray-700 block">Nội dung mô tả:</span>
                <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                  {selectedListing.description}
                </p>
              </div>

              {/* Owner Info */}
              <div className="p-3 bg-blue-50/60 rounded-xl flex items-center justify-between text-blue-900">
                <div>
                  <span className="font-semibold block">Người nộp tin:</span>
                  <span>
                    {selectedListing.owner_name} ({selectedListing.owner_phone})
                  </span>
                </div>
                <span className="text-xs font-bold text-amber-700 bg-amber-100 px-2.5 py-1 rounded-full">
                  Chờ duyệt
                </span>
              </div>

              {/* Reject Reason input box */}
              {rejectMode && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl space-y-2 animate-in fade-in">
                  <label className="font-bold text-red-800 block">
                    Nhập lý do từ chối (Chủ tin sẽ nhận được phản hồi này):
                  </label>
                  <textarea
                    rows={3}
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Ví dụ: Ảnh mờ, thiếu thông tin pháp lý rõ ràng hoặc sai mức giá thị trường..."
                    className="w-full p-2.5 bg-white border border-red-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 resize-none text-xs text-gray-800"
                  />
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="p-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between shrink-0">
              <button
                type="button"
                onClick={() => setSelectedListing(null)}
                className="px-4 py-2 border border-gray-300 rounded-xl text-gray-700 hover:bg-white text-xs font-medium"
              >
                Đóng
              </button>

              <div className="flex items-center space-x-2">
                {!rejectMode ? (
                  <>
                    <button
                      type="button"
                      onClick={() => setRejectMode(true)}
                      className="px-4 py-2 border border-red-300 text-red-600 hover:bg-red-50 rounded-xl text-xs font-semibold flex items-center space-x-1"
                    >
                      <X className="w-4 h-4" />
                      <span>Từ chối tin</span>
                    </button>

                    <button
                      type="button"
                      disabled={actionLoading}
                      onClick={handleApprove}
                      className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-1 shadow-xs disabled:opacity-50"
                    >
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Check className="w-4 h-4" />
                      )}
                      <span>Phê duyệt xuất bản</span>
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={() => setRejectMode(false)}
                      className="px-4 py-2 border border-gray-300 text-gray-600 rounded-xl text-xs font-medium"
                    >
                      Hủy bỏ
                    </button>

                    <button
                      type="button"
                      disabled={actionLoading}
                      onClick={handleReject}
                      className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-semibold flex items-center space-x-1 shadow-xs disabled:opacity-50"
                    >
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <X className="w-4 h-4" />
                      )}
                      <span>Xác nhận từ chối</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
