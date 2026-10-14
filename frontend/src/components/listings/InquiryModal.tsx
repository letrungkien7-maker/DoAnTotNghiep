import React, { useState } from 'react';
import { X, Send, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { interactionService } from '@/services/interaction.service';
import { getErrorMessage } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

interface InquiryModalProps {
  listingId: number;
  listingTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

export const InquiryModal: React.FC<InquiryModalProps> = ({
  listingId,
  listingTitle,
  isOpen,
  onClose,
}) => {
  const { user } = useAuth();
  const [senderName, setSenderName] = useState(user?.full_name || '');
  const [senderPhone, setSenderPhone] = useState(user?.phone_number || '');
  const [senderEmail, setSenderEmail] = useState(user?.email || '');
  const [message, setMessage] = useState(
    'Tôi rất quan tâm đến bất động sản này. Xin vui lòng liên hệ tư vấn thêm thông tin chi tiết.'
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!senderName.trim() || !senderPhone.trim() || !message.trim()) {
      setError('Vui lòng điền đầy đủ họ tên, số điện thoại và nội dung tin nhắn.');
      return;
    }

    setLoading(true);
    try {
      await interactionService.sendInquiry({
        listing_id: listingId,
        sender_name: senderName.trim(),
        sender_phone: senderPhone.trim(),
        sender_email: senderEmail.trim() || undefined,
        message: message.trim(),
      });
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onClose();
      }, 2000);
    } catch (err) {
      setError(getErrorMessage(err, 'Không thể gửi yêu cầu tư vấn. Vui lòng thử lại sau.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-2xs animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-gray-100 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 p-1 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-lg font-bold text-gray-900 mb-1">Yêu cầu tư vấn bất động sản</h3>
        <p className="text-xs text-gray-500 mb-4 line-clamp-1">Tin: {listingTitle}</p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {success ? (
          <div className="py-8 text-center space-y-3">
            <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto animate-bounce" />
            <h4 className="font-semibold text-gray-900">Gửi yêu cầu thành công!</h4>
            <p className="text-xs text-gray-500">
              Người đăng bất động sản sẽ sớm nhận được thông tin và liên hệ lại với bạn.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
            <div>
              <label className="block font-medium text-gray-700 mb-1">
                Họ và tên của bạn <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={senderName}
                onChange={(e) => setSenderName(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ví dụ: Nguyễn Văn A"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block font-medium text-gray-700 mb-1">
                  Số điện thoại <span className="text-red-500">*</span>
                </label>
                <input
                  type="tel"
                  value={senderPhone}
                  onChange={(e) => setSenderPhone(e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0912 345 678"
                />
              </div>

              <div>
                <label className="block font-medium text-gray-700 mb-1">Email nhận tin</label>
                <input
                  type="email"
                  value={senderEmail}
                  onChange={(e) => setSenderEmail(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="email@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block font-medium text-gray-700 mb-1">
                Nội dung cần tư vấn <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                placeholder="Nhập câu hỏi hoặc thời gian thuận tiện để liên hệ..."
              />
            </div>

            <div className="pt-2 flex justify-end space-x-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition"
              >
                Hủy bỏ
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-5 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 transition flex items-center space-x-1.5 shadow-xs"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Đang gửi...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Gửi yêu cầu</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
