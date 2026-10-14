import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Building2, Lock, Mail, AlertCircle, Loader2, Sparkles, UserCheck } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { getErrorMessage } from '@/services/api';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login({ email: email.trim(), password });
      navigate(redirectPath, { replace: true });
    } catch (err) {
      setError(getErrorMessage(err, 'Đăng nhập không thành công. Vui lòng kiểm tra lại thông tin.'));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6">
        {/* Logo & Heading */}
        <div className="text-center">
          <Link to="/" className="inline-flex items-center space-x-2 text-blue-600 font-bold text-2xl">
            <div className="p-2 bg-blue-600 text-white rounded-xl shadow-xs">
              <Building2 className="w-6 h-6" />
            </div>
            <span className="text-gray-900">BDS<span className="text-blue-600">Smart</span></span>
          </Link>
          <h2 className="mt-4 text-2xl font-bold text-gray-900 tracking-tight">
            Đăng nhập hệ thống
          </h2>
          <p className="mt-1 text-xs text-gray-500">
            Truy cập nền tảng để đăng tin, lưu yêu thích và quản lý giao dịch
          </p>
        </div>

        {/* Demo Fast Login Buttons */}
        <div className="bg-blue-50/80 border border-blue-200 rounded-2xl p-4 space-y-2.5">
          <div className="flex items-center space-x-1.5 text-xs font-bold text-blue-900">
            <Sparkles className="w-4 h-4 text-amber-500" />
            <span>Đăng nhập nhanh tài khoản thử nghiệm (1-Click Fill):</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleDemoFill('admin@bds.vn', 'AdminPass123!')}
              className="p-2 bg-white border border-blue-200 rounded-xl hover:bg-blue-100 hover:border-blue-400 font-medium text-slate-800 transition text-center shadow-2xs flex flex-col items-center"
            >
              <UserCheck className="w-3.5 h-3.5 text-amber-600 mb-0.5" />
              <span className="font-bold text-[11px]">Admin</span>
              <span className="text-[10px] text-gray-400">admin@bds.vn</span>
            </button>

            <button
              type="button"
              onClick={() => handleDemoFill('chutin1@bds.vn', 'Password123!')}
              className="p-2 bg-white border border-blue-200 rounded-xl hover:bg-blue-100 hover:border-blue-400 font-medium text-slate-800 transition text-center shadow-2xs flex flex-col items-center"
            >
              <UserCheck className="w-3.5 h-3.5 text-blue-600 mb-0.5" />
              <span className="font-bold text-[11px]">Chủ tin 1</span>
              <span className="text-[10px] text-gray-400">chutin1@bds.vn</span>
            </button>

            <button
              type="button"
              onClick={() => handleDemoFill('khachxem@bds.vn', 'Password123!')}
              className="p-2 bg-white border border-blue-200 rounded-xl hover:bg-blue-100 hover:border-blue-400 font-medium text-slate-800 transition text-center shadow-2xs flex flex-col items-center"
            >
              <UserCheck className="w-3.5 h-3.5 text-green-600 mb-0.5" />
              <span className="font-bold text-[11px]">Khách xem</span>
              <span className="text-[10px] text-gray-400">khachxem@bds.vn</span>
            </button>
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-sm">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Địa chỉ Email <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="name@example.com"
                  className="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Mật khẩu <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition flex items-center justify-center space-x-2 shadow-xs disabled:opacity-50 text-sm mt-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang đăng nhập...</span>
                </>
              ) : (
                <span>Đăng nhập</span>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-gray-500">
            Chưa có tài khoản?{' '}
            <Link to="/register" className="font-semibold text-blue-600 hover:underline">
              Đăng ký tài khoản mới
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
