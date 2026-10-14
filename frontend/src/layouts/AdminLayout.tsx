import React from 'react';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck, Users, ArrowLeft, LogOut, Building2 } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

export const AdminLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navItems = [
    {
      title: 'Kiểm duyệt tin đăng',
      path: '/admin/moderation',
      icon: <ShieldCheck className="w-5 h-5" />,
    },
    {
      title: 'Quản lý người dùng',
      path: '/admin/users',
      icon: <Users className="w-5 h-5" />,
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col md:flex-row font-sans">
      {/* Sidebar */}
      <aside className="w-full md:w-64 bg-slate-900 text-white shrink-0 flex flex-col justify-between">
        <div>
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2">
              <div className="p-1.5 bg-blue-600 rounded-lg">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg tracking-tight">Admin Portal</span>
            </Link>
          </div>

          <div className="p-4 border-b border-slate-800">
            <p className="text-xs text-slate-400">Đang đăng nhập:</p>
            <p className="text-sm font-semibold truncate text-slate-200">{user?.full_name}</p>
            <span className="inline-block mt-1 px-2 py-0.5 text-[11px] font-semibold rounded bg-amber-500/20 text-amber-400">
              Quản trị viên (ADMIN)
            </span>
          </div>

          <nav className="p-3 space-y-1">
            {navItems.map((item) => {
              const active = location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                    active
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  {item.icon}
                  <span>{item.title}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-slate-800 space-y-2">
          <Link
            to="/"
            className="flex items-center space-x-2 text-xs text-slate-400 hover:text-white transition py-1.5"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Quay lại trang người dùng</span>
          </Link>
          <button
            onClick={handleLogout}
            className="w-full flex items-center space-x-2 text-xs text-red-400 hover:text-red-300 transition py-1.5"
          >
            <LogOut className="w-4 h-4" />
            <span>Đăng xuất</span>
          </button>
        </div>
      </aside>

      {/* Main Admin Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between shadow-2xs">
          <h1 className="text-lg font-semibold text-gray-800">Bảng điều khiển Quản trị</h1>
          <span className="text-xs text-gray-500">Môi trường: FastAPI + PostgreSQL</span>
        </header>

        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
