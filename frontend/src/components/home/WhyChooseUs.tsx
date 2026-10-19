import React from 'react';
import { Bot, ShieldCheck, Lock, Globe2, Sparkles, CheckCircle2 } from 'lucide-react';

export const WhyChooseUs: React.FC = () => {
  const features = [
    {
      icon: <Bot className="w-6 h-6 text-blue-600" />,
      bg: 'bg-blue-50',
      title: 'Trợ Lý Ảo AI Đột Phá',
      description:
        'Tương tác thông minh bằng ngôn ngữ tự nhiên. AI tự động bóc tách nhu cầu ngân sách, vị trí và gợi ý bất động sản phù hợp tức thì.',
      highlights: ['Chatbot tương tác 24/7', 'Hiểu văn cảnh tiếng Việt', 'Gợi ý cá nhân hóa'],
    },
    {
      icon: <ShieldCheck className="w-6 h-6 text-emerald-600" />,
      bg: 'bg-emerald-50',
      title: 'Kiểm Duyệt Pháp Lý Chặt Chẽ',
      description:
        'Tin đăng được thẩm định rõ ràng về hình ảnh, sổ đỏ/hồng và thông tin thực tế trước khi xuất hiện công khai trên sàn.',
      highlights: ['Tối thiểu 3 ảnh chất lượng', 'Xác thực sổ đỏ/sổ hồng', 'Chặn tin ảo triệt để'],
    },
    {
      icon: <Lock className="w-6 h-6 text-purple-600" />,
      bg: 'bg-purple-50',
      title: 'Bảo Vệ Quyền Riêng Tư',
      description:
        'Cơ chế che số điện thoại thông minh chỉ mở khi người dùng xác thực, ngăn chặn triệt để tình trạng telesale và rò rỉ dữ liệu.',
      highlights: ['Bảo mật số điện thoại', 'Ngăn chặn spam cuộc gọi', 'Tôn trọng thông tin cá nhân'],
    },
    {
      icon: <Globe2 className="w-6 h-6 text-amber-600" />,
      bg: 'bg-amber-50',
      title: 'Mạng Lưới Toàn Diện 63 Tỉnh',
      description:
        'Cơ sở dữ liệu phủ sóng đầy đủ 63 tỉnh thành Việt Nam, từ đại đô thị đến vùng kinh tế ven biển và cao nguyên nghỉ dưỡng.',
      highlights: ['Đa dạng loại hình BĐS', 'Bộ lọc địa lý chi tiết', 'Cập nhật giá liên tục'],
    },
  ];

  return (
    <section className="bg-slate-50/80 py-16 border-y border-gray-200/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-xs font-bold uppercase tracking-wider mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Giá trị cốt lõi</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            Tại Sao Hàng Ngàn Khách Hàng Tin Chọn BDSSmart?
          </h2>
          <p className="text-sm text-gray-600 mt-2">
            Giải pháp giao dịch bất động sản thời đại số - Minh bạch, Nhanh chóng và Đáng tin cậy
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((item, idx) => (
            <div
              key={idx}
              className="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-xs hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                <div className={`p-3.5 ${item.bg} w-fit rounded-xl mb-4`}>
                  {item.icon}
                </div>
                <h3 className="font-bold text-base text-gray-900 mb-2">
                  {item.title}
                </h3>
                <p className="text-xs text-gray-600 leading-relaxed mb-4">
                  {item.description}
                </p>
              </div>

              <div className="pt-4 border-t border-gray-100 space-y-1.5">
                {item.highlights.map((h, i) => (
                  <div key={i} className="flex items-center space-x-2 text-[11px] text-gray-700 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                    <span>{h}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
