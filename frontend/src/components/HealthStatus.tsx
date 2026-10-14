import React, { useEffect, useState } from 'react';
import { checkHealth } from '@/services/api';
import { HealthResponse } from '@/types';
import { Activity, Database, Server, RefreshCw, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

export const HealthStatus: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await checkHealth();
      setHealth(data);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Không thể kết nối đến Backend FastAPI';
      setError(errorMessage);
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 max-w-2xl mx-auto my-8">
      <div className="flex items-center justify-between pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-3">
          <Activity className="w-6 h-6 text-brand-600" />
          <h2 className="text-xl font-semibold text-slate-800">
            Tình trạng Hệ thống (Health Check)
          </h2>
        </div>
        <button
          onClick={fetchHealth}
          disabled={loading}
          className="flex items-center space-x-1.5 px-3 py-1.5 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Làm mới</span>
        </button>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Backend Server Status */}
        <div className="p-4 rounded-lg border border-slate-100 bg-slate-50 flex items-start space-x-3">
          <Server className="w-5 h-5 text-slate-600 mt-0.5" />
          <div className="flex-1">
            <div className="text-sm font-medium text-slate-500">Backend API (FastAPI)</div>
            {loading ? (
              <div className="text-sm text-slate-400 mt-1">Đang kiểm tra...</div>
            ) : health ? (
              <div className="flex items-center space-x-1.5 mt-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span className="text-sm font-semibold text-emerald-700">Đang hoạt động (v{health.version})</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1.5 mt-1">
                <XCircle className="w-4 h-4 text-rose-600" />
                <span className="text-sm font-semibold text-rose-700">Mất kết nối</span>
              </div>
            )}
          </div>
        </div>

        {/* Database Status */}
        <div className="p-4 rounded-lg border border-slate-100 bg-slate-50 flex items-start space-x-3">
          <Database className="w-5 h-5 text-slate-600 mt-0.5" />
          <div className="flex-1">
            <div className="text-sm font-medium text-slate-500">Database (PostgreSQL)</div>
            {loading ? (
              <div className="text-sm text-slate-400 mt-1">Đang kiểm tra...</div>
            ) : health?.database.status === 'connected' ? (
              <div className="flex items-center space-x-1.5 mt-1">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span className="text-sm font-semibold text-emerald-700">
                  Đã kết nối ({health.database.latency_ms} ms)
                </span>
              </div>
            ) : (
              <div className="flex items-center space-x-1.5 mt-1">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-semibold text-amber-700">Chưa kết nối DB</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Diagnostic details */}
      {error && (
        <div className="mt-4 p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700 font-mono">
          Lỗi: {error}
        </div>
      )}

      {health?.database.error && (
        <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 font-mono">
          Chi tiết DB: {health.database.error}
        </div>
      )}

      {health && (
        <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-400 flex justify-between">
          <span>Môi trường: {health.environment}</span>
          <span>Thời gian kiểm tra: {new Date(health.timestamp).toLocaleTimeString()}</span>
        </div>
      )}
    </div>
  );
};
