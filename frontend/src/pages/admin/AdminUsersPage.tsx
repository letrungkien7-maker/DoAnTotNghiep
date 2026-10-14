import React, { useEffect, useState, useCallback } from 'react';
import {
  Users,
  Search,
  Shield,
  UserCheck,
  UserX,
  Phone,
  Mail,
  Loader2,
} from 'lucide-react';
import { PaginatedData, User } from '@/types';
import { adminService } from '@/services/admin.service';
import { formatDate } from '@/utils/formatters';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Pagination } from '@/components/common/Pagination';
import { EmptyState } from '@/components/common/EmptyState';

export const AdminUsersPage: React.FC = () => {
  const [data, setData] = useState<PaginatedData<User>>({
    items: [],
    total: 0,
    page: 1,
    size: 10,
    total_pages: 1,
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [search, setSearch] = useState<string>('');
  const [roleFilter, setRoleFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [actionId, setActionId] = useState<number | null>(null);

  const fetchUsers = useCallback(
    async (page = 1) => {
      setLoading(true);
      try {
        const res = await adminService.listUsers({
          page,
          size: 10,
          search: search.trim() || undefined,
          role: roleFilter || undefined,
          is_active: statusFilter === '' ? undefined : statusFilter === 'true',
        });
        setData(res);
      } catch {
        setData({ items: [], total: 0, page: 1, size: 10, total_pages: 1 });
      } finally {
        setLoading(false);
      }
    },
    [search, roleFilter, statusFilter]
  );

  useEffect(() => {
    fetchUsers(1);
  }, [fetchUsers]);

  const handleToggleStatus = async (user: User) => {
    const nextStatus = !user.is_active;
    const confirmMsg = nextStatus
      ? `Bạn có chắc muốn mở khóa tài khoản của "${user.full_name}"?`
      : `Bạn có chắc muốn khóa tài khoản của "${user.full_name}"? Người dùng này sẽ không thể đăng nhập hoặc đăng tin.`;

    if (!confirm(confirmMsg)) return;

    setActionId(user.id);
    try {
      await adminService.updateUserStatus(user.id, nextStatus);
      setData((prev) => ({
        ...prev,
        items: prev.items.map((u) => (u.id === user.id ? { ...u, is_active: nextStatus } : u)),
      }));
    } catch {
      // Ignore
    } finally {
      setActionId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900 flex items-center space-x-2">
            <Users className="w-6 h-6 text-blue-600" />
            <span>Quản lý tài khoản người dùng</span>
          </h2>
          <p className="text-xs text-gray-500 mt-1">
            Tổng cộng: <strong className="text-blue-600">{data.total}</strong> tài khoản trong hệ thống
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-gray-200 shadow-xs flex flex-col sm:flex-row gap-3 text-xs">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm theo tên, email hoặc số điện thoại..."
            className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
        </div>

        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 bg-white"
        >
          <option value="">Tất cả vai trò</option>
          <option value="USER">Thành viên (USER)</option>
          <option value="ADMIN">Quản trị viên (ADMIN)</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 bg-white"
        >
          <option value="">Tất cả trạng thái</option>
          <option value="true">Đang hoạt động</option>
          <option value="false">Đã bị khóa</option>
        </select>
      </div>

      {/* Users Table */}
      {loading ? (
        <LoadingSpinner message="Đang tải danh sách người dùng..." />
      ) : data.items.length === 0 ? (
        <EmptyState
          icon={<Users className="w-10 h-10 text-gray-400" />}
          title="Không tìm thấy tài khoản nào"
          description="Không có tài khoản nào phù hợp với bộ lọc tìm kiếm hiện tại."
        />
      ) : (
        <div className="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-xs">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-gray-600">
              <thead className="bg-gray-50 border-b border-gray-200 text-gray-700 font-bold uppercase tracking-wider text-[11px]">
                <tr>
                  <th className="py-3 px-4">Người dùng</th>
                  <th className="py-3 px-4">Số điện thoại</th>
                  <th className="py-3 px-4">Vai trò</th>
                  <th className="py-3 px-4">Ngày tham gia</th>
                  <th className="py-3 px-4">Trạng thái</th>
                  <th className="py-3 px-4 text-center">Thao tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.items.map((u) => (
                  <tr key={u.id} className="hover:bg-blue-50/30 transition">
                    <td className="py-3 px-4 flex items-center space-x-3">
                      <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold shrink-0">
                        {u.full_name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <span className="font-bold text-gray-900 block truncate">{u.full_name}</span>
                        <span className="text-[11px] text-gray-400 flex items-center space-x-1">
                          <Mail className="w-3 h-3" />
                          <span>{u.email}</span>
                        </span>
                      </div>
                    </td>

                    <td className="py-3 px-4 font-medium text-gray-700">
                      <span className="flex items-center space-x-1">
                        <Phone className="w-3 h-3 text-gray-400" />
                        <span>{u.phone_number}</span>
                      </span>
                    </td>

                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          u.role === 'ADMIN'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}
                      >
                        <Shield className="w-3 h-3" />
                        <span>{u.role}</span>
                      </span>
                    </td>

                    <td className="py-3 px-4 text-gray-400">{formatDate(u.created_at)}</td>

                    <td className="py-3 px-4">
                      {u.is_active ? (
                        <span className="inline-flex items-center space-x-1 text-green-700 text-xs font-semibold">
                          <span className="w-2 h-2 rounded-full bg-green-500"></span>
                          <span>Hoạt động</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1 text-red-600 text-xs font-semibold">
                          <span className="w-2 h-2 rounded-full bg-red-500"></span>
                          <span>Đã khóa</span>
                        </span>
                      )}
                    </td>

                    <td className="py-3 px-4 text-center">
                      {u.role !== 'ADMIN' && (
                        <button
                          disabled={actionId === u.id}
                          onClick={() => handleToggleStatus(u)}
                          className={`px-3 py-1.5 rounded-lg font-semibold text-xs transition inline-flex items-center space-x-1 ${
                            u.is_active
                              ? 'border border-red-200 text-red-600 hover:bg-red-50'
                              : 'bg-green-600 text-white hover:bg-green-700'
                          }`}
                        >
                          {actionId === u.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : u.is_active ? (
                            <>
                              <UserX className="w-3.5 h-3.5" />
                              <span>Khóa</span>
                            </>
                          ) : (
                            <>
                              <UserCheck className="w-3.5 h-3.5" />
                              <span>Mở khóa</span>
                            </>
                          )}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Pagination
            currentPage={data.page}
            totalPages={data.total_pages}
            onPageChange={(page) => fetchUsers(page)}
          />
        </div>
      )}
    </div>
  );
};
