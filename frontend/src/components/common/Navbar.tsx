import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Building2,
  Heart,
  PlusCircle,
  User as UserIcon,
  LogOut,
  ShieldCheck,
  FileText,
  MessageSquare,
  Menu,
  X,
  ChevronDown,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    setDropdownOpen(false);
    await logout();
    navigate('/');
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Main Nav */}
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2 text-blue-600 font-bold text-xl tracking-tight">
              <div className="p-2 bg-blue-600 text-white rounded-lg shadow-xs">
                <Building2 className="w-5 h-5" />
              </div>
              <span className="text-gray-900">BDS<span className="text-blue-600">Smart</span></span>
            </Link>

            <div className="hidden md:flex items-center space-x-6 text-sm font-medium text-gray-700">
              <Link to="/" className="hover:text-blue-600 transition">Trang chủ</Link>
              <Link to="/search" className="hover:text-blue-600 transition">Tìm kiếm</Link>
              <Link to="/search?transaction_type=SALE" className="hover:text-blue-600 transition">Mua bán</Link>
              <Link to="/search?transaction_type=RENT" className="hover:text-blue-600 transition">Cho thuê</Link>
            </div>
          </div>

          {/* Right Action buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  to="/favorites"
                  className="p-2 text-gray-600 hover:text-red-500 hover:bg-gray-50 rounded-full transition relative"
                  title="Tin đã lưu"
                >
                  <Heart className="w-5 h-5" />
                </Link>

                <Link
                  to="/post-listing"
                  className="inline-flex items-center space-x-1.5 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 shadow-xs transition"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Đăng tin</span>
                </Link>

                {/* User Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setDropdownOpen(!dropdownOpen)}
                    className="flex items-center space-x-2 p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition"
                  >
                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm">
                      {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <span className="text-sm font-medium text-gray-700 max-w-[120px] truncate">
                      {user?.full_name}
                    </span>
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  </button>

                  {dropdownOpen && (
                    <div
                      className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-150"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <div className="px-4 py-2 border-b border-gray-100">
                        <p className="text-xs text-gray-500">Đăng nhập với</p>
                        <p className="text-sm font-semibold text-gray-800 truncate">{user?.email}</p>
                        <span className="inline-block mt-1 px-2 py-0.5 text-xs rounded-full font-medium bg-blue-50 text-blue-700">
                          {user?.role === 'ADMIN' ? 'Quản trị viên' : 'Thành viên'}
                        </span>
                      </div>

                      <Link
                        to="/profile"
                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <UserIcon className="w-4 h-4 text-gray-500" />
                        <span>Hồ sơ cá nhân</span>
                      </Link>

                      <Link
                        to="/my-listings"
                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <FileText className="w-4 h-4 text-gray-500" />
                        <span>Quản lý tin đăng</span>
                      </Link>

                      <Link
                        to="/inquiries"
                        className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        <MessageSquare className="w-4 h-4 text-gray-500" />
                        <span>Khách liên hệ</span>
                      </Link>

                      {isAdmin && (
                        <>
                          <div className="border-t border-gray-100 my-1" />
                          <div className="px-4 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                            Quản trị
                          </div>
                          <Link
                            to="/admin/moderation"
                            className="flex items-center space-x-2 px-4 py-2 text-sm text-amber-700 bg-amber-50/50 hover:bg-amber-100/50"
                          >
                            <ShieldCheck className="w-4 h-4 text-amber-600" />
                            <span>Kiểm duyệt tin đăng</span>
                          </Link>
                          <Link
                            to="/admin/users"
                            className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                          >
                            <UserIcon className="w-4 h-4 text-gray-500" />
                            <span>Quản lý người dùng</span>
                          </Link>
                        </>
                      )}

                      <div className="border-t border-gray-100 my-1" />
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 text-left"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Đăng xuất</span>
                      </button>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-blue-600 transition"
                >
                  Đăng nhập
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-medium text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition"
                >
                  Đăng ký
                </Link>
                <Link
                  to="/post-listing"
                  className="inline-flex items-center space-x-1.5 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 shadow-xs transition"
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Đăng tin</span>
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu toggle */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white px-4 pt-2 pb-6 space-y-3">
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-blue-600"
          >
            Trang chủ
          </Link>
          <Link
            to="/search"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-blue-600"
          >
            Tìm kiếm BĐS
          </Link>
          <Link
            to="/search?transaction_type=SALE"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-blue-600"
          >
            Mua bán
          </Link>
          <Link
            to="/search?transaction_type=RENT"
            onClick={() => setMobileMenuOpen(false)}
            className="block py-2 text-base font-medium text-gray-700 hover:text-blue-600"
          >
            Cho thuê
          </Link>

          {isAuthenticated ? (
            <div className="pt-4 border-t border-gray-100 space-y-2">
              <div className="text-sm font-semibold text-gray-900">{user?.full_name}</div>
              <div className="text-xs text-gray-500">{user?.email}</div>

              <Link
                to="/post-listing"
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full py-2 text-center bg-blue-600 text-white rounded-lg font-medium text-sm mt-3"
              >
                + Đăng tin mới
              </Link>
              <Link
                to="/my-listings"
                onClick={() => setMobileMenuOpen(false)}
                className="block py-2 text-sm text-gray-700 hover:text-blue-600"
              >
                Quản lý tin đăng
              </Link>
              <Link
                to="/favorites"
                onClick={() => setMobileMenuOpen(false)}
                className="block py-2 text-sm text-gray-700 hover:text-blue-600"
              >
                Tin đã lưu
              </Link>
              <Link
                to="/inquiries"
                onClick={() => setMobileMenuOpen(false)}
                className="block py-2 text-sm text-gray-700 hover:text-blue-600"
              >
                Khách liên hệ
              </Link>
              <Link
                to="/profile"
                onClick={() => setMobileMenuOpen(false)}
                className="block py-2 text-sm text-gray-700 hover:text-blue-600"
              >
                Hồ sơ cá nhân
              </Link>

              {isAdmin && (
                <Link
                  to="/admin/moderation"
                  onClick={() => setMobileMenuOpen(false)}
                  className="block py-2 text-sm text-amber-700 font-medium"
                >
                  Kiểm duyệt tin đăng (Admin)
                </Link>
              )}

              <button
                onClick={handleLogout}
                className="w-full text-left py-2 text-sm text-red-600 font-medium"
              >
                Đăng xuất
              </button>
            </div>
          ) : (
            <div className="pt-4 border-t border-gray-100 space-y-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full py-2 text-center text-sm font-medium border border-gray-300 rounded-lg"
              >
                Đăng nhập
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="block w-full py-2 text-center text-sm font-medium bg-blue-600 text-white rounded-lg"
              >
                Đăng ký tài khoản
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};
