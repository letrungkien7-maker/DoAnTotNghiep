import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Search,
  Building,
  Home,
  Compass,
  Layers,
  Sparkles,
  ShieldCheck,
  TrendingUp,
  ArrowRight,
} from 'lucide-react';
import { Category, ListingCard as ListingCardType } from '@/types';
import { listingService } from '@/services/listing.service';
import { categoryService } from '@/services/category.service';
import { ListingCard } from '@/components/listings/ListingCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

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
    <div className="space-y-12 pb-16">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950 text-white py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#3b82f6_1px,transparent_1px)] [background-size:16px_16px]" />

        <div className="max-w-4xl mx-auto relative z-10 text-center space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-400/30 text-xs font-semibold">
            <Sparkles className="w-4 h-4 text-amber-300" />
            <span>Nền tảng BĐS tích hợp Chatbot AI & Gợi ý thông minh</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Khám phá Ngôi nhà Mơ ước <br className="hidden sm:inline" />
            với <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-amber-300">Công nghệ Trí tuệ Nhân tạo</span>
          </h1>

          <p className="text-sm sm:text-base text-gray-300 max-w-2xl mx-auto">
            Hàng ngàn tin đăng được kiểm duyệt minh bạch, tìm kiếm nhanh chóng và hỗ trợ tư vấn 24/7 từ trợ lý thông minh.
          </p>

          {/* Quick Search Card */}
          <div className="bg-white p-3 sm:p-4 rounded-2xl shadow-2xl text-gray-900 max-w-2xl mx-auto border border-white/20">
            {/* Tabs */}
            <div className="flex space-x-2 mb-3">
              <button
                type="button"
                onClick={() => setTransactionType('SALE')}
                className={`px-4 py-1.5 text-xs font-bold rounded-lg transition ${
                  transactionType === 'SALE'
                    ? 'bg-blue-600 text-white shadow-xs'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                Nhà đất Bán
              </button>
              <button
                type="button"
                onClick={() => setTransactionType('RENT')}
                className={`px-4 py-1.5 text-xs font-bold rounded-lg transition ${
                  transactionType === 'RENT'
                    ? 'bg-emerald-600 text-white shadow-xs'
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
                  placeholder="Nhập địa điểm, dự án hoặc nhu cầu tìm kiếm..."
                  className="w-full pl-10 pr-4 py-3 text-sm bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white"
                />
              </div>
              <button
                type="submit"
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-xl transition flex items-center justify-center space-x-2 shadow-md shrink-0"
              >
                <Search className="w-4 h-4" />
                <span>Tìm kiếm</span>
              </button>
            </form>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Khám phá theo Loại hình</h2>
            <p className="text-xs text-gray-500 mt-1">Các danh mục bất động sản phổ biến và được quan tâm nhất</p>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {categories.map((cat) => (
            <Link
              key={cat.id}
              to={`/search?category_id=${cat.id}`}
              className="p-5 bg-white border border-gray-200 rounded-xl shadow-2xs hover:shadow-md hover:border-blue-400 transition-all text-center flex flex-col items-center group"
            >
              <div className="p-3 bg-gray-50 rounded-xl mb-3 group-hover:scale-110 group-hover:bg-blue-50 transition-transform">
                {getCategoryIcon(cat.slug)}
              </div>
              <h3 className="font-semibold text-gray-800 text-sm group-hover:text-blue-600 transition">
                {cat.name}
              </h3>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured / Recent Listings */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Bất động sản Nổi bật Mới nhất</h2>
            <p className="text-xs text-gray-500 mt-1">Tin đăng đã được ban quản trị kiểm duyệt và xác thực</p>
          </div>
          <Link
            to="/search"
            className="inline-flex items-center space-x-1 text-sm font-semibold text-blue-600 hover:text-blue-700"
          >
            <span>Xem tất cả</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <LoadingSpinner message="Đang tải danh sách bất động sản..." />
        ) : featuredListings.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
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

      {/* Value Propositions */}
      <section className="bg-blue-50/60 py-12 border-y border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-10">
            <h2 className="text-2xl font-bold text-gray-900">Lợi ích vượt trội cho Người dùng</h2>
            <p className="text-xs text-gray-600 mt-1">Hệ thống thông minh toàn diện dành cho cả Người mua và Người bán</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-2xs space-y-3">
              <div className="p-3 bg-blue-100 text-blue-600 w-fit rounded-xl">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-base text-gray-900">Kiểm duyệt Tin đăng Nghiêm ngặt</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Mọi tin đăng phải có tối thiểu 3 ảnh chất lượng cao và được Admin duyệt kỹ lưỡng trước khi xuất hiện trên trang tìm kiếm.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-2xs space-y-3">
              <div className="p-3 bg-indigo-100 text-indigo-600 w-fit rounded-xl">
                <Sparkles className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-base text-gray-900">Trợ lý AI Chatbot Tư vấn 24/7</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Tự động hiểu ngôn ngữ tự nhiên, gợi ý bất động sản chuẩn xác theo ngân sách và vị trí mà không cần tìm kiếm thủ công.
              </p>
            </div>

            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-2xs space-y-3">
              <div className="p-3 bg-emerald-100 text-emerald-600 w-fit rounded-xl">
                <TrendingUp className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-base text-gray-900">Bảo mật Thông tin & Quyền riêng tư</h3>
              <p className="text-xs text-gray-600 leading-relaxed">
                Che số điện thoại đối với khách vãng lai để tránh spam, chỉ cho phép thành viên đã xác thực xem thông tin liên hệ đầy đủ.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
