import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { HealthStatus } from '@/components/HealthStatus';
import { Building2, Bot, Sparkles, Layers, ShieldCheck } from 'lucide-react';

const HomePage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="text-center space-y-4">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-brand-50 border border-brand-200 text-brand-700 rounded-full text-xs font-semibold tracking-wide uppercase">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Đồ án Tốt nghiệp - Khởi tạo Khung Dự án</span>
        </div>
        <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight sm:text-5xl">
          Hệ Thống Bất Động Sản Thông Minh
        </h1>
        <p className="max-w-2xl mx-auto text-lg text-slate-600">
          Nền tảng kinh doanh bất động sản tích hợp Trợ lý ảo AI Chatbot và Hệ thống Gợi ý thông minh.
        </p>
      </div>

      {/* Health Status Dashboard Component */}
      <HealthStatus />

      {/* Architectural Pillars Preview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 bg-blue-100 text-brand-600 rounded-lg flex items-center justify-center mb-4">
            <Building2 className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-2">Sàn Giao Dịch BĐS</h3>
          <p className="text-sm text-slate-600">
            Quản lý tin đăng đa trạng thái, tìm kiếm nâng cao với bộ lọc đa tiêu chí và định danh RBAC.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center mb-4">
            <Bot className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-2">Trợ Lý Ảo Chatbot AI</h3>
          <p className="text-sm text-slate-600">
            Tư vấn nhu cầu nhà ở tự nhiên, trích xuất tham số và truy vấn dữ liệu thực tế từ Database.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="w-10 h-10 bg-emerald-100 text-emerald-600 rounded-lg flex items-center justify-center mb-4">
            <Sparkles className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-slate-900 mb-2">Gợi Ý Thông Minh</h3>
          <p className="text-sm text-slate-600">
            Đề xuất BĐS tương đồng qua Content-Based Cosine Similarity và cá nhân hóa theo lịch sử tương tác.
          </p>
        </div>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50 flex flex-col justify-between">
        <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-2.5">
              <Building2 className="w-6 h-6 text-brand-600" />
              <span className="font-bold text-lg text-slate-900">BDS SmartPlatform</span>
            </Link>
            <div className="flex items-center space-x-4 text-sm text-slate-600">
              <span className="flex items-center space-x-1">
                <Layers className="w-4 h-4 text-slate-400" />
                <span>React + Vite + FastAPI</span>
              </span>
              <span className="flex items-center space-x-1 text-emerald-600 font-medium">
                <ShieldCheck className="w-4 h-4" />
                <span>Boilerplate Ready</span>
              </span>
            </div>
          </div>
        </header>

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>

        <footer className="bg-white border-t border-slate-200 py-6 text-center text-sm text-slate-500">
          © 2026 Đồ án tốt nghiệp: Hệ thống Bất động sản tích hợp Chatbot & Gợi ý thông minh.
        </footer>
      </div>
    </Router>
  );
};

export default App;
