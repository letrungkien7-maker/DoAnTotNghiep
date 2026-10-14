import React, { useState } from 'react';
import { User, Phone, Mail, Shield, Calendar, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { authService } from '@/services/auth.service';
import { getErrorMessage } from '@/services/api';
import { formatDate } from '@/utils/formatters';

export const ProfilePage: React.FC = () => {
  const { user, refreshProfile } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phoneNumber, setPhoneNumber] = useState(user?.phone_number || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      await authService.updateProfile({
        full_name: fullName.trim(),
        phone_number: phoneNumber.trim(),
      });
      await refreshProfile();
      setSuccess('Cập nhật thông tin hồ sơ thành công!');
    } catch (err) {
      setError(getErrorMessage(err, 'Không thể cập nhật hồ sơ. Vui lòng thử lại.'));
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Hồ sơ cá nhân</h1>
        <p className="text-xs text-gray-500 mt-1">
          Quản lý thông tin tài khoản và thông tin liên hệ được hiển thị khi bạn đăng tin
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* User Info Card */}
        <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs text-center space-y-4">
          <div className="w-20 h-20 rounded-full bg-blue-600 text-white font-bold text-2xl flex items-center justify-center mx-auto shadow-md">
            {user.full_name.charAt(0).toUpperCase()}
          </div>

          <div>
            <h3 className="font-bold text-gray-900 text-lg">{user.full_name}</h3>
            <p className="text-xs text-gray-500">{user.email}</p>
          </div>

          <div className="pt-3 border-t border-gray-100 flex justify-center">
            <span
              className={`inline-flex items-center space-x-1 px-3 py-1 text-xs font-semibold rounded-full ${
                user.role === 'ADMIN'
                  ? 'bg-amber-100 text-amber-800'
                  : 'bg-blue-100 text-blue-800'
              }`}
            >
              <Shield className="w-3.5 h-3.5" />
              <span>{user.role === 'ADMIN' ? 'Quản trị viên hệ thống' : 'Thành viên'}</span>
            </span>
          </div>

          <div className="text-left text-xs text-gray-600 space-y-2 pt-2">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-gray-400" />
              <span>Tham gia: {formatDate(user.created_at)}</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-green-500" />
              <span>Trạng thái: Hoạt động bình thường</span>
            </div>
          </div>
        </div>

        {/* Update Form Card */}
        <div className="md:col-span-2 bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
          <h2 className="text-base font-bold text-gray-900 mb-4">Cập nhật thông tin</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 text-xs rounded-xl flex items-start space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold text-gray-700 mb-1">Địa chỉ Email (Định danh)</label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  value={user.email}
                  disabled
                  className="w-full pl-9 pr-3 py-2.5 bg-gray-100 text-gray-500 border border-gray-200 rounded-xl cursor-not-allowed"
                />
              </div>
              <p className="text-[10px] text-gray-400 mt-1">Email được cố định để xác thực bảo mật.</p>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Họ và tên hiển thị <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Số điện thoại liên hệ <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Phone className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>
              <p className="text-[10px] text-gray-400 mt-1">
                Số điện thoại sẽ hiển thị cho khách hàng khi họ xem tin đăng của bạn.
              </p>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition flex items-center space-x-2 shadow-xs disabled:opacity-50 text-sm"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Đang lưu...</span>
                  </>
                ) : (
                  <span>Lưu thay đổi</span>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
