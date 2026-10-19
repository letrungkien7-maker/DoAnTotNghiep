import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  Building,
  Home,
  Compass,
  Layers,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Flame,
  PlusCircle,
  MessageSquare,
} from 'lucide-react';
import { Category, ListingCard as ListingCardType } from '@/types';
import { listingService } from '@/services/listing.service';
import { categoryService } from '@/services/category.service';
import { ListingCard } from '@/components/listings/ListingCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { StatsRibbon } from '@/components/home/StatsRibbon';
import { CitySpotlight } from '@/components/home/CitySpotlight';
import { MortgageCalculator } from '@/components/home/MortgageCalculator';
import { WhyChooseUs } from '@/components/home/WhyChooseUs';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<Category[]>([]);
  const [featuredListings, setFeaturedListings] = useState<ListingCardType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [transactionType, setTransactionType] = useState<'SALE' | 'RENT'>('SALE');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [catData, listingData] = await Promise.all([
          categoryService.getCategories(),
          listingService.searchListings({ size: 8, sort_by: 'newest' }),
        ]);
        setCategories(catData);
        setFeaturedListings(listingData.items);
      } catch {
        // Fallback or error handled silently
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleHeroSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const query = new URLSearchParams();
    if (searchKeyword.trim()) query.set('keyword', searchKeyword.trim());
    query.set('transaction_type', transactionType);
    navigate(`/search?${query.toString()}`);
  };

  const handleQuickTagClick = (keyword: string, province?: string) => {
    const query = new URLSearchParams();
    if (keyword) query.set('keyword', keyword);
    if (province) query.set('province', province);
    query.set('transaction_type', transactionType);
    navigate(`/search?${query.toString()}`);
  };

  const getCategoryIcon = (slug: string) => {
    switch (slug) {
      case 'can-ho-chung-cu':
        return <Building className="w-6 h-6 text-blue-600" />;
      case 'nha-rieng-nha-pho':
        return <Home className="w-6 h-6 text-emerald-600" />;
      case 'biet-thu-nghi-duong':
        return <Compass className="w-6 h-6 text-purple-600" />;
      case 'dat-nen-du-an':
        return <Layers className="w-6 h-6 text-amber-600" />;
      default:
        return <Building className="w-6 h-6 text-blue-600" />;
    }
  };

  return (
    <div className="space-y-16 pb-20 overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white pt-24 pb-28 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Glow backdrop circles */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/15 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute top-1/3 right-10 w-[300px] h-[300px] bg-indigo-500/15 blur-[100px] rounded-full pointer-events-none" />

        <div className="max-w-4xl mx-auto relative z-10 text-center space-y-6">
          {/* Top Pill */}
          <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-blue-500/15 text-blue-300 border border-blue-400/30 text-xs font-semibold backdrop-blur-md shadow-xs">
            <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
            <span>Nền tảng BĐS Thông Minh Tích Hợp Trợ Lý AI • 63 Tỉnh Thành</span>
          </div>

          {/* Heading */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight">
            Khám phá Ngôi nhà Mơ ước <br />
            với <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-amber-300">Trí Tuệ Nhân Tạo AI</span>
          </h1>

          <p className="text-sm sm:text-base text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Hàng ngàn tin đăng được kiểm duyệt pháp lý minh bạch, gợi ý thông minh theo nhu cầu và tư vấn 24/7 từ linh vật AI.
          </p>

          {/* Search Glass Container */}
          <div className="bg-white/95 backdrop-blur-xl p-3 sm:p-5 rounded-3xl shadow-2xl text-gray-900 max-w-2xl mx-auto border border-white/40">
            {/* Tabs */}
            <div className="flex space-x-2 mb-3">
              <button
                type="button"
                onClick={() => setTransactionType('SALE')}
                className={`px-5 py-2 text-xs sm:text-sm font-bold rounded-xl transition-all cursor-pointer ${
                  transactionType === 'SALE'
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Nhà đất Bán
              </button>
              <button
                type="button"
                onClick={() => setTransactionType('RENT')}
                className={`px-5 py-2 text-xs sm:text-sm font-bold rounded-xl transition-all cursor-pointer ${
                  transactionType === 'RENT'
                    ? 'bg-emerald-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Nhà đất Cho thuê
              </button>
            </div>

            {/* Input & Submit */}
            <form onSubmit={handleHeroSearch} className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <Search className="w-5 h-5 absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  value={searchKeyword}
                  onChange={(e) => setSearchKeyword(e.target.value)}
                  placeholder="Nhập địa điểm, dự án, tên đường hoặc nhu cầu (VD: Căn hộ 2PN view biển)..."
                  className="w-full pl-10 pr-4 py-3.5 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white transition"
                />
              </div>
              <button
                type="submit"
                className="px-6 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl transition flex items-center justify-center space-x-2 shadow-md hover:shadow-lg shrink-0 cursor-pointer"
              >
                <Search className="w-4 h-4" />
                <span>Tìm kiếm</span>
              </button>
            </form>

            {/* Quick Trending Tags */}
            <div className="flex items-center flex-wrap gap-1.5 pt-3 mt-1 border-t border-gray-100 text-xs">
              <span className="text-gray-400 font-semibold flex items-center space-x-1 mr-1">
                <Flame className="w-3.5 h-3.5 text-amber-500" />
                <span>Xu hướng:</span>
              </span>
              <button
                type="button"
                onClick={() => handleQuickTagClick('', 'Thành phố Hà Nội')}
                className="px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-blue-50 hover:text-blue-600 text-gray-700 font-medium transition cursor-pointer"
              >
                Hà Nội
              </button>
              <button
                type="button"
                onClick={() => handleQuickTagClick('', 'Thành phố Hồ Chí Minh')}
                className="px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-blue-50 hover:text-blue-600 text-gray-700 font-medium transition cursor-pointer"
              >
                TP. HCM
              </button>
              <button
                type="button"
                onClick={() => handleQuickTagClick('', 'Thành phố Đà Nẵng')}
                className="px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-blue-50 hover:text-blue-600 text-gray-700 font-medium transition cursor-pointer"
              >
                Đà Nẵng
              </button>
              <button
                type="button"
                onClick={() => handleQuickTagClick('Chung cư')}
                className="px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-blue-50 hover:text-blue-600 text-gray-700 font-medium transition cursor-pointer"
              >
                Chung cư cao cấp
              </button>
              <button
                type="button"
                onClick={() => handleQuickTagClick('Biệt thự')}
                className="px-2.5 py-1 rounded-lg bg-gray-100 hover:bg-blue-50 hover:text-blue-600 text-gray-700 font-medium transition cursor-pointer"
              >
                Biệt thự nghỉ dưỡng
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Counter Ribbon */}
      <StatsRibbon />

      {/* Categories Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-600 text-xs font-bold uppercase tracking-wider mb-2">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Phân loại phổ biến</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
              Khám Phá Theo Loại Hình Bất Động Sản
            </h2>
            <p className="text-sm text-gray-500 mt-1">Các danh mục bất động sản đa dạng đáp ứng trọn vẹn nhu cầu của bạn</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/search?category_id=${cat.id}`}
              className="p-6 bg-white border border-gray-200/80 rounded-2xl shadow-xs hover:shadow-xl hover:border-blue-400 hover:-translate-y-1 transition-all duration-300 text-center flex flex-col items-center group relative overflow-hidden"
            >
              <div className="p-4 bg-gray-50 rounded-2xl mb-3.5 group-hover:scale-110 group-hover:bg-blue-50 transition-all duration-300">
                {getCategoryIcon(cat.slug)}
              </div>
              <h3 className="font-bold text-gray-900 text-sm group-hover:text-blue-600 transition">
                {cat.name}
              </h3>
              <span className="text-[11px] font-semibold text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity mt-2 flex items-center space-x-0.5">
                <span>Xem tin đăng</span>
                <ArrowRight className="w-3 h-3" />
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured / Recent Listings */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 text-xs font-bold uppercase tracking-wider mb-2">
              <Flame className="w-3.5 h-3.5" />
              <span>Cập nhật mới nhất</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
              Bất Động Sản Nổi Bật Được Kiểm Duyệt
            </h2>
            <p className="text-sm text-gray-500 mt-1">Tin đăng đã xác thực pháp lý & hình ảnh thực tế từ ban quản trị</p>
          </div>
          <Link
            to="/search"
            className="inline-flex items-center space-x-1 text-sm font-bold text-blue-600 hover:text-blue-700 transition"
          >
            <span>Xem tất cả danh sách</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <LoadingSpinner message="Đang tải danh sách bất động sản..." />
        ) : featuredListings.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-gray-200 shadow-xs">
            <p className="text-sm text-gray-500">Chưa có tin đăng nào khả dụng trên hệ thống.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {featuredListings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </section>

      {/* City Spotlight Section */}
      <CitySpotlight />

      {/* Interactive Mortgage Loan Calculator */}
      <MortgageCalculator />

      {/* Why Choose Us */}
      <WhyChooseUs />

      {/* Call To Action Banner */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-800 rounded-3xl p-8 sm:p-12 text-white shadow-xl flex flex-col md:flex-row items-center justify-between gap-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-xl space-y-3 text-center md:text-left">
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight">
              Bạn Có Bất Động Sản Cần Giao Dịch?
            </h2>
            <p className="text-sm text-blue-100 leading-relaxed">
              Tiếp cận hàng ngàn khách hàng tiềm năng mỗi ngày với hệ thống kiểm duyệt tin đăng chuyên nghiệp và trợ lý AI thông minh hỗ trợ kết nối.
            </p>
          </div>

          <div className="relative z-10 flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            <Link
              to="/post-listing"
              className="px-6 py-3.5 bg-white text-blue-700 hover:bg-blue-50 font-bold text-sm rounded-xl transition shadow-lg flex items-center justify-center space-x-2"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Đăng tin miễn phí ngay</span>
            </Link>
            <button
              type="button"
              onClick={() => {
                const chatbotToggle = document.querySelector('button[title*="Chat"]') as HTMLButtonElement;
                if (chatbotToggle) chatbotToggle.click();
              }}
              className="px-6 py-3.5 bg-blue-900/60 hover:bg-blue-900 text-white font-bold text-sm rounded-xl transition border border-white/20 flex items-center justify-center space-x-2 cursor-pointer"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Trò chuyện với AI</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
