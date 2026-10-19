import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowUpRight, Compass } from 'lucide-react';

interface CityInfo {
  id: string;
  name: string;
  provinceParam: string;
  badge: string;
  tagline: string;
  image: string;
  colSpan?: string;
}

export const CitySpotlight: React.FC = () => {
  const cities: CityInfo[] = [
    {
      id: 'hcm',
      name: 'TP. Hồ Chí Minh',
      provinceParam: 'Thành phố Hồ Chí Minh',
      badge: 'Đô thị hạt nhân',
      tagline: 'Trung tâm tài chính, thương mại & căn hộ hiện đại bậc nhất',
      image: 'https://images.unsplash.com/photo-1583417319070-4a69db38a482?w=800&auto=format&fit=crop&q=80',
      colSpan: 'sm:col-span-2 md:col-span-2 lg:col-span-2',
    },
    {
      id: 'hn',
      name: 'Thủ Đô Hà Nội',
      provinceParam: 'Thành phố Hà Nội',
      badge: 'Trung tâm văn hóa',
      tagline: 'Thị trường bất động sản nghìn năm văn hiến, giá trị sinh lời bền vững',
      image: 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&auto=format&fit=crop&q=80',
      colSpan: 'sm:col-span-1 md:col-span-1 lg:col-span-1',
    },
    {
      id: 'dn',
      name: 'Đà Nẵng',
      provinceParam: 'Thành phố Đà Nẵng',
      badge: 'Đáng sống số 1',
      tagline: 'Thiên đường du lịch ven biển, biệt thự và căn hộ view sông Hàn',
      image: 'https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800&auto=format&fit=crop&q=80',
      colSpan: 'sm:col-span-1 md:col-span-1 lg:col-span-1',
    },
    {
      id: 'kh',
      name: 'Khánh Hòa',
      provinceParam: 'Tỉnh Khánh Hòa',
      badge: 'Vịnh biển ngọc',
      tagline: 'Căn hộ nghỉ dưỡng Nha Trang, bãi tắm thơ mộng & khí hậu ấm áp',
      image: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&auto=format&fit=crop&q=80',
      colSpan: 'sm:col-span-1 md:col-span-1 lg:col-span-1',
    },
    {
      id: 'ld',
      name: 'Lâm Đồng',
      provinceParam: 'Tỉnh Lâm Đồng',
      badge: 'Thành phố mộng mơ',
      tagline: 'Biệt thự đồi thông Đà Lạt, khí hậu mát mẻ và không gian sống thanh bình',
      image: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800&auto=format&fit=crop&q=80',
      colSpan: 'sm:col-span-1 md:col-span-1 lg:col-span-1',
    },
    {
      id: 'qn',
      name: 'Quảng Ninh',
      provinceParam: 'Tỉnh Quảng Ninh',
      badge: 'Kỳ quan di sản',
      tagline: 'Đô thị vịnh biển Hạ Long, bất động sản du lịch và kinh tế đêm sôi động',
      image: 'https://images.unsplash.com/photo-1528127269322-539801943592?w=800&auto=format&fit=crop&q=80',
      colSpan: 'sm:col-span-1 md:col-span-1 lg:col-span-1',
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
        <div>
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-bold uppercase tracking-wider mb-2">
            <Compass className="w-3.5 h-3.5" />
            <span>Thị trường tâm điểm</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            Khám phá BĐS theo Địa phương Trọng điểm
          </h2>
          <p className="text-sm text-gray-500 mt-1 max-w-xl">
            Các trung tâm đô thị lớn và vùng du lịch nghỉ dưỡng sôi động nhất toàn quốc
          </p>
        </div>

        <Link
          to="/search"
          className="inline-flex items-center space-x-1 text-sm font-bold text-blue-600 hover:text-blue-700 transition"
        >
          <span>Xem tất cả 63 tỉnh thành</span>
          <ArrowUpRight className="w-4 h-4" />
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {cities.map((city) => (
          <Link
            key={city.id}
            to={`/search?province=${encodeURIComponent(city.provinceParam)}`}
            className="group relative h-72 sm:h-80 rounded-2xl overflow-hidden shadow-md hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 block border border-gray-100"
          >
            {/* Background Image */}
            <img
              src={city.image}
              alt={city.name}
              className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
              loading="lazy"
            />

            {/* Gradient Mask */}
            <div className="absolute inset-0 bg-gradient-to-t from-gray-950 via-gray-950/40 to-transparent" />

            {/* Floating Top Badge */}
            <div className="absolute top-4 left-4 z-10">
              <span className="px-3 py-1 text-xs font-semibold rounded-full bg-white/20 backdrop-blur-md text-white border border-white/20 shadow-xs">
                {city.badge}
              </span>
            </div>

            {/* Hover arrow button */}
            <div className="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-white/20 backdrop-blur-md border border-white/30 flex items-center justify-center text-white group-hover:bg-blue-600 group-hover:border-blue-600 transition-colors shadow-xs">
              <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </div>

            {/* Card Content at bottom */}
            <div className="absolute bottom-0 inset-x-0 p-6 z-10 text-white space-y-1.5">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-white group-hover:text-blue-300 transition-colors">
                {city.name}
              </h3>
              <p className="text-xs text-gray-300 line-clamp-2 leading-relaxed">
                {city.tagline}
              </p>
              <div className="pt-2 flex items-center text-xs font-semibold text-amber-300 group-hover:translate-x-1 transition-transform">
                <span>Khám phá tin đăng tại đây</span>
                <span className="ml-1">→</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
};
