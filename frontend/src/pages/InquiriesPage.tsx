import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  MessageSquare,
  Phone,
  Mail,
  Calendar,
  CheckCircle,
  Clock,
  XCircle,
  ExternalLink,
} from 'lucide-react';
import { Inquiry } from '@/types';
import { interactionService } from '@/services/interaction.service';
import { formatDate } from '@/utils/formatters';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';

export const InquiriesPage: React.FC = () => {
  const [inquiries, setInquiries] = useState<Inquiry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [updatingId, setUpdatingId] = useState<number | null>(null);

  const fetchInquiries = async () => {
    setLoading(true);
    try {
      const data = await interactionService.getReceivedInquiries();
      setInquiries(data);
    } catch {
      setInquiries([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInquiries();
  }, []);

  const handleStatusUpdate = async (id: number, newStatus: 'CONTACTED' | 'CLOSED') => {
    setUpdatingId(id);
    try {
      const updated = await interactionService.updateInquiryStatus(id, newStatus);
      setInquiries((prev) =>
        prev.map((item) => (item.id === id ? { ...item, status: updated.status } : item))
      );
    } catch {
      // Ignore
    } finally {
      setUpdatingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <Clock className="w-3 h-3" />
            <span>Chờ liên hệ</span>
          </span>
        );
      case 'CONTACTED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            <CheckCircle className="w-3 h-3" />
            <span>Đã liên hệ</span>
          </span>
        );
      case 'CLOSED':
        return (
          <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-100 text-gray-600 border border-gray-200">
            <XCircle className="w-3 h-3" />
            <span>Đã hoàn tất / Đóng</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center space-x-2">
        <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
          <MessageSquare className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Yêu cầu tư vấn từ khách hàng</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Danh sách khách hàng để lại thông tin liên hệ cho các bất động sản của bạn
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Đang tải danh sách yêu cầu tư vấn..." />
      ) : inquiries.length === 0 ? (
        <EmptyState
          icon={<MessageSquare className="w-10 h-10 text-blue-400" />}
          title="Chưa có yêu cầu tư vấn nào"
          description="Khi khách hàng gửi form liên hệ trên tin đăng của bạn, thông tin sẽ được cập nhật ngay tại đây."
        />
      ) : (
        <div className="space-y-4">
          {inquiries.map((inq) => (
            <div
              key={inq.id}
              className="bg-white p-5 rounded-2xl border border-gray-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-2 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-bold text-gray-900 text-base">{inq.sender_name}</h3>
                  {getStatusBadge(inq.status)}
                  <span className="text-xs text-gray-400 flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{formatDate(inq.created_at)}</span>
                  </span>
                </div>

                <div className="text-xs text-gray-600 flex items-center space-x-1 font-medium">
                  <span>Quan tâm tin đăng:</span>
                  <Link
                    to={`/listings/${inq.listing_id}`}
                    className="text-blue-600 hover:underline inline-flex items-center space-x-1 line-clamp-1 max-w-md"
                  >
                    <span>{inq.listing_title}</span>
                    <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>

                <div className="p-3 bg-gray-50 rounded-xl border border-gray-100 text-xs text-gray-700 italic">
                  "{inq.message}"
                </div>

                <div className="flex flex-wrap items-center gap-4 text-xs pt-1">
                  <a
                    href={`tel:${inq.sender_phone}`}
                    className="flex items-center space-x-1 font-semibold text-emerald-600 hover:underline"
                  >
                    <Phone className="w-3.5 h-3.5" />
                    <span>{inq.sender_phone}</span>
                  </a>

                  {inq.sender_email && (
                    <a
                      href={`mailto:${inq.sender_email}`}
                      className="flex items-center space-x-1 text-gray-600 hover:text-blue-600"
                    >
                      <Mail className="w-3.5 h-3.5 text-gray-400" />
                      <span>{inq.sender_email}</span>
                    </a>
                  )}
                </div>
              </div>

              {/* Status Update Actions */}
              <div className="flex flex-row md:flex-col gap-2 shrink-0 border-t md:border-t-0 md:border-l border-gray-100 pt-3 md:pt-0 md:pl-4">
                {inq.status === 'PENDING' && (
                  <button
                    disabled={updatingId === inq.id}
                    onClick={() => handleStatusUpdate(inq.id, 'CONTACTED')}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold transition"
                  >
                    Đánh dấu đã liên hệ
                  </button>
                )}

                {inq.status !== 'CLOSED' && (
                  <button
                    disabled={updatingId === inq.id}
                    onClick={() => handleStatusUpdate(inq.id, 'CLOSED')}
                    className="px-3 py-1.5 border border-gray-300 hover:bg-gray-100 text-gray-700 rounded-lg text-xs font-medium transition"
                  >
                    Đóng yêu cầu
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
