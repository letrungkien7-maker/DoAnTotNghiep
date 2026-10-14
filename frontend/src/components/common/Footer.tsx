import React from 'react';
import { Building2, Mail, Phone, MapPin, ShieldCheck, Cpu } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-gray-300 pt-12 pb-8 border-t border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Info */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 text-white font-bold text-xl">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <span>BDS<span className="text-blue-500">Smart</span></span>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed">
              Hệ thống kinh doanh bất động sản thông minh tích hợp trợ lý ảo AI và thuật toán gợi ý cá nhân hóa. Đồ án tốt nghiệp Công nghệ Thông tin.
            </p>
            <div className="flex items-center space-x-2 text-xs text-blue-400 bg-blue-950/60 p-2 rounded-lg border border-blue-900">
              <Cpu className="w-4 h-4" />
              <span>AI Chatbot & Smart Recommendation Ready</span>
            </div>
          </div>

          {/* Quick links */}
          <div>
            <h4 className="text-white text-sm font-semibold uppercase tracking-wider mb-4">
              Khám phá
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/search?transaction_type=SALE" className="hover:text-white transition">
                  Bất động sản mua bán
                </Link>
              </li>
              <li>
                <Link to="/search?transaction_type=RENT" className="hover:text-white transition">
                  Bất động sản cho thuê
                </Link>
              </li>
              <li>
                <Link to="/search" className="hover:text-white transition">
                  Tìm kiếm nâng cao
                </Link>
              </li>
              <li>
                <Link to="/post-listing" className="hover:text-white transition">
                  Đăng tin bất động sản
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Policy */}
          <div>
            <h4 className="text-white text-sm font-semibold uppercase tracking-wider mb-4">
              Quy định & Bảo mật
            </h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center space-x-1.5">
                <ShieldCheck className="w-4 h-4 text-green-500" />
                <span>Quy trình kiểm duyệt tin đăng</span>
              </li>
              <li>Bảo mật thông tin liên hệ</li>
              <li>Điều khoản sử dụng dịch vụ</li>
              <li>Giải quyết khiếu nại báo cáo</li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white text-sm font-semibold uppercase tracking-wider mb-4">
              Liên hệ đồ án
            </h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li className="flex items-center space-x-2">
                <MapPin className="w-4 h-4 text-gray-400" />
                <span>Hà Nội, Việt Nam</span>
              </li>
              <li className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-gray-400" />
                <span>admin@bds.vn</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4 text-gray-400" />
                <span>1900 6868 (Hotline Demo)</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-gray-800 text-center text-xs text-gray-500">
          <p>© 2026 BDS Smart Platform. Đề tài tốt nghiệp: Hệ thống kinh doanh bất động sản tích hợp Chatbot và gợi ý thông minh.</p>
        </div>
      </div>
    </footer>
  );
};
