import React from 'react';
import { MapPin, ShieldCheck, Bot, Zap } from 'lucide-react';

export const StatsRibbon: React.FC = () => {
  const stats = [
    {
      icon: <MapPin className="w-6 h-6 text-blue-500" />,
      number: '63',
      unit: 'Tỉnh thành',
      title: 'Phủ sóng toàn quốc',
      desc: 'Dữ liệu BĐS Bắc - Trung - Nam',
    },
    {
      icon: <ShieldCheck className="w-6 h-6 text-emerald-500" />,
      number: '100%',
      unit: 'Xác thực',
      title: 'Pháp lý minh bạch',
      desc: 'Kiểm duyệt ảnh thật & thông tin',
    },
    {
      icon: <Bot className="w-6 h-6 text-purple-500" />,
      number: '24/7',
      unit: 'Trợ lý AI',
      title: 'Tư vấn thông minh',
      desc: 'Gợi ý chuẩn xác theo nhu cầu',
    },
    {
      icon: <Zap className="w-6 h-6 text-amber-500" />,
      number: '< 30ms',
      unit: 'Phản hồi',
      title: 'Tốc độ tối ưu',
      desc: 'Hạ tầng Cloud siêu tốc mượt mà',
    },
  ];

  return (
    <div className="relative -mt-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-20">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((item, idx) => (
          <div
            key={idx}
            className="group relative overflow-hidden bg-white/95 backdrop-blur-md p-5 rounded-2xl border border-gray-100 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
          >
            {/* Subtle glow border */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/5 to-purple-500/0 opacity-0 group-hover:opacity-100 transition-opacity" />

            <div className="relative z-10 flex items-start space-x-4">
              <div className="p-3 rounded-xl bg-gray-50 border border-gray-100 group-hover:scale-110 group-hover:bg-blue-50 transition-all duration-300 shrink-0">
                {item.icon}
              </div>
              <div className="min-w-0">
                <div className="flex items-baseline space-x-1.5">
                  <span className="text-2xl sm:text-3xl font-black text-gray-900 tracking-tight">
                    {item.number}
                  </span>
                  <span className="text-xs font-bold text-blue-600 uppercase tracking-wider">
                    {item.unit}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-gray-800 mt-0.5 truncate">
                  {item.title}
                </h4>
                <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">
                  {item.desc}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
