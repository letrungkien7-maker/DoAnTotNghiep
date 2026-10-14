import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  MapPin,
  BedDouble,
  Bath,
  Compass,
  FileCheck,
  Calendar,
  Eye,
  Heart,
  Phone,
  MessageCircle,
  Share2,
  ArrowLeft,
  ShieldCheck,
  Lock,
  CheckCircle,
  Sparkles,
} from 'lucide-react';
import { ListingCard as ListingCardType, ListingDetail } from '@/types';
import { listingService } from '@/services/listing.service';
import { interactionService } from '@/services/interaction.service';
import { recommendationService } from '@/services/recommendation.service';
import { formatDate, formatPrice, getStatusBadge } from '@/utils/formatters';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ListingCard } from '@/components/listings/ListingCard';
import { InquiryModal } from '@/components/listings/InquiryModal';
import { useAuth } from '@/context/AuthContext';

export const ListingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [listing, setListing] = useState<ListingDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState<number>(0);
  const [isFavorited, setIsFavorited] = useState<boolean>(false);
  const [inquiryModalOpen, setInquiryModalOpen] = useState<boolean>(false);
  const [copyNotice, setCopyNotice] = useState<boolean>(false);
  const [similarListings, setSimilarListings] = useState<ListingCardType[]>([]);

  useEffect(() => {
    if (!id) return;
    const fetchDetail = async () => {
      setLoading(true);
      try {
        const [data, similarData] = await Promise.all([
          listingService.getListingDetail(Number(id)),
          recommendationService.getSimilarListings(Number(id), 4).catch(() => ({ items: [] })),
        ]);
        setListing(data);
        setIsFavorited(data.is_favorite);
        setSimilarListings(similarData.items);
      } catch {
        navigate('/search');
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id, navigate]);

  const handleToggleFavorite = async () => {
    if (!listing) return;
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    try {
      const res = await interactionService.toggleFavorite(listing.id);
      setIsFavorited(res.is_favorited);
    } catch {
      // Ignore
    }
  };

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopyNotice(true);
    setTimeout(() => setCopyNotice(false), 2500);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16">
        <LoadingSpinner message="Đang tải thông tin chi tiết bất động sản..." />
      </div>
    );
  }

  if (!listing) return null;

  const images = listing.images.length > 0
    ? listing.images
    : [{ image_url: 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800', public_id: 'default' }];

  const currentImage = images[selectedImageIndex] || images[0];
  const isOwner = user?.id === listing.owner_id;
  const statusBadge = getStatusBadge(listing.status);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Breadcrumb & Navigation */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-2">
          <Link to="/search" className="flex items-center space-x-1 hover:text-blue-600 transition">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Quay lại tìm kiếm</span>
          </Link>
          <span>/</span>
          <span className="text-gray-700 font-medium">{listing.category_name}</span>
          <span>/</span>
          <span className="text-gray-400 truncate max-w-[200px]">{listing.province}</span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleShare}
            className="flex items-center space-x-1 px-3 py-1.5 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>{copyNotice ? 'Đã sao chép liên kết!' : 'Chia sẻ'}</span>
          </button>
          <button
            onClick={handleToggleFavorite}
            className={`flex items-center space-x-1 px-3 py-1.5 border rounded-lg transition ${
              isFavorited
                ? 'border-red-200 bg-red-50 text-red-600'
                : 'border-gray-200 hover:bg-gray-50 text-gray-700'
            }`}
          >
            <Heart className={`w-3.5 h-3.5 ${isFavorited ? 'fill-red-500 text-red-500' : ''}`} />
            <span>{isFavorited ? 'Đã lưu' : 'Lưu tin'}</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Left 2 Cols (Media & Details) + Right 1 Col (Seller Contact) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          {/* Image Gallery */}
          <div className="space-y-3">
            <div className="relative aspect-[16/10] bg-gray-900 rounded-2xl overflow-hidden shadow-md">
              <img
                src={currentImage.image_url}
                alt={listing.title}
                className="w-full h-full object-cover"
              />
              <span
                className={`absolute top-4 left-4 text-xs font-semibold px-3 py-1.5 rounded-lg shadow-md ${
                  listing.transaction_type === 'SALE'
                    ? 'bg-blue-600 text-white'
                    : 'bg-emerald-600 text-white'
                }`}
              >
                {listing.transaction_type === 'SALE' ? 'Nhà đất Bán' : 'Cho thuê'}
              </span>

              {listing.status !== 'APPROVED' && (
                <span
                  className={`absolute top-4 right-4 text-xs font-bold px-3 py-1.5 rounded-lg border shadow-md ${statusBadge.bg} ${statusBadge.text}`}
                >
                  {statusBadge.label}
                </span>
              )}
            </div>

            {/* Thumbnail Strip */}
            {images.length > 1 && (
              <div className="flex space-x-2 overflow-x-auto pb-2">
                {images.map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedImageIndex(idx)}
                    className={`w-20 h-14 rounded-lg overflow-hidden border-2 shrink-0 transition ${
                      selectedImageIndex === idx ? 'border-blue-600 scale-95 shadow-sm' : 'border-transparent opacity-70 hover:opacity-100'
                    }`}
                  >
                    <img src={img.image_url} alt={`Ảnh ${idx + 1}`} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Title & Core Price */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-4">
            <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-gray-100 pb-4">
              <div>
                <span className="text-3xl font-extrabold text-blue-600">
                  {formatPrice(listing.price, listing.price_unit, listing.transaction_type)}
                </span>
                <span className="text-gray-500 text-sm ml-2 font-medium">
                  • {listing.area} m² ({Math.round(listing.price / listing.area).toLocaleString('vi-VN')} đ/m²)
                </span>
              </div>

              <div className="flex items-center space-x-3 text-xs text-gray-500">
                <span className="flex items-center space-x-1">
                  <Eye className="w-3.5 h-3.5" />
                  <span>{listing.view_count} lượt xem</span>
                </span>
                <span>•</span>
                <span className="flex items-center space-x-1">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Đăng ngày: {formatDate(listing.published_at || listing.created_at)}</span>
                </span>
              </div>
            </div>

            <h1 className="text-xl sm:text-2xl font-bold text-gray-900 leading-snug">
              {listing.title}
            </h1>

            <div className="flex items-start space-x-2 text-sm text-gray-600">
              <MapPin className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <span>
                {listing.address_text}, {listing.ward ? `${listing.ward}, ` : ''}
                {listing.district}, {listing.province}
              </span>
            </div>
          </div>

          {/* Key Attributes Grid */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs">
            <h2 className="text-base font-bold text-gray-900 mb-4">Đặc điểm bất động sản</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div className="p-3 bg-gray-50 rounded-xl space-y-1">
                <span className="text-gray-500">Diện tích</span>
                <p className="font-bold text-sm text-gray-800">{listing.area} m²</p>
              </div>

              <div className="p-3 bg-gray-50 rounded-xl space-y-1">
                <span className="text-gray-500 flex items-center space-x-1">
                  <BedDouble className="w-3.5 h-3.5" />
                  <span>Phòng ngủ</span>
                </span>
                <p className="font-bold text-sm text-gray-800">{listing.bedrooms ?? '---'} phòng</p>
              </div>

              <div className="p-3 bg-gray-50 rounded-xl space-y-1">
                <span className="text-gray-500 flex items-center space-x-1">
                  <Bath className="w-3.5 h-3.5" />
                  <span>Phòng tắm</span>
                </span>
                <p className="font-bold text-sm text-gray-800">{listing.bathrooms ?? '---'} phòng</p>
              </div>

              <div className="p-3 bg-gray-50 rounded-xl space-y-1">
                <span className="text-gray-500 flex items-center space-x-1">
                  <Compass className="w-3.5 h-3.5" />
                  <span>Hướng nhà</span>
                </span>
                <p className="font-bold text-sm text-gray-800">{listing.direction || 'Không xác định'}</p>
              </div>

              <div className="p-3 bg-gray-50 rounded-xl space-y-1 sm:col-span-2">
                <span className="text-gray-500 flex items-center space-x-1">
                  <FileCheck className="w-3.5 h-3.5" />
                  <span>Tình trạng pháp lý</span>
                </span>
                <p className="font-bold text-sm text-gray-800">{listing.legal_status || 'Đang cập nhật'}</p>
              </div>

              <div className="p-3 bg-gray-50 rounded-xl space-y-1 sm:col-span-2">
                <span className="text-gray-500">Mã tin đăng</span>
                <p className="font-bold text-sm text-gray-800">#{listing.id}</p>
              </div>
            </div>
          </div>

          {/* Description */}
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-3">
            <h2 className="text-base font-bold text-gray-900">Mô tả chi tiết</h2>
            <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
              {listing.description}
            </div>
          </div>

          {/* Features / Amenities */}
          {listing.features && listing.features.length > 0 && (
            <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-3">
              <h2 className="text-base font-bold text-gray-900">Tiện ích & Điểm nổi bật</h2>
              <div className="flex flex-wrap gap-2">
                {listing.features.map((feat, i) => (
                  <span
                    key={i}
                    className="flex items-center space-x-1 px-3 py-1.5 bg-blue-50 text-blue-700 border border-blue-100 rounded-lg text-xs font-medium"
                  >
                    <CheckCircle className="w-3.5 h-3.5 text-blue-600" />
                    <span>{feat}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar: Seller Card & Actions */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-xs space-y-5 sticky top-20">
            <div className="flex items-center space-x-3 pb-4 border-b border-gray-100">
              <div className="w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-lg shadow-xs">
                {listing.owner_name.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-xs text-gray-500">Người đăng tin</p>
                <h3 className="font-bold text-gray-900 text-base">{listing.owner_name}</h3>
                <span className="text-[11px] text-green-600 flex items-center space-x-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  <span>Tài khoản đã xác thực</span>
                </span>
              </div>
            </div>

            {/* Phone contact section with BR-05 rule */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-700">Số điện thoại liên hệ</label>

              {isAuthenticated ? (
                <a
                  href={`tel:${listing.owner_phone}`}
                  className="w-full flex items-center justify-center space-x-2 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-xs transition"
                >
                  <Phone className="w-4 h-4" />
                  <span>{listing.owner_phone}</span>
                </a>
              ) : (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl space-y-2 text-center">
                  <div className="flex items-center justify-center space-x-1 text-sm font-bold text-gray-800">
                    <Lock className="w-4 h-4 text-amber-600" />
                    <span>{listing.owner_phone}</span>
                  </div>
                  <p className="text-[11px] text-gray-600">
                    Số điện thoại được che để bảo vệ riêng tư. Vui lòng đăng nhập để xem đầy đủ.
                  </p>
                  <Link
                    to={`/login?redirect=${encodeURIComponent(window.location.pathname)}`}
                    className="inline-block px-3 py-1 text-xs font-semibold text-blue-600 hover:underline"
                  >
                    Đăng nhập ngay
                  </Link>
                </div>
              )}
            </div>

            {/* Submit Consultation Inquiry Button */}
            {!isOwner ? (
              <button
                onClick={() => setInquiryModalOpen(true)}
                className="w-full flex items-center justify-center space-x-2 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-xs transition text-sm"
              >
                <MessageCircle className="w-4 h-4" />
                <span>Yêu cầu tư vấn / Hẹn xem nhà</span>
              </button>
            ) : (
              <div className="p-3 bg-blue-50 border border-blue-200 text-blue-700 text-xs rounded-xl text-center font-medium">
                Đây là tin đăng của chính bạn. Bạn có thể vào mục{' '}
                <Link to="/my-listings" className="font-bold underline">
                  Quản lý tin đăng
                </Link>{' '}
                để chỉnh sửa.
              </div>
            )}

            {/* Guarantee note */}
            <div className="pt-3 border-t border-gray-100 text-[11px] text-gray-400 space-y-1">
              <p>• Tin đăng được kiểm duyệt nội dung theo tiêu chuẩn BDS Smart.</p>
              <p>• Không đặt cọc hoặc chuyển khoản khi chưa xác thực thông tin thực tế.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recommended Similar Properties Section */}
      {similarListings.length > 0 && (
        <section className="pt-8 border-t border-gray-200 space-y-4">
          <div className="flex items-center space-x-2">
            <div className="p-1.5 bg-blue-100 text-blue-600 rounded-lg">
              <Sparkles className="w-4 h-4 text-amber-500" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">Bất động sản tương tự dành cho bạn</h2>
              <p className="text-xs text-gray-500">
                Thuật toán Content-Based AI gợi ý dựa trên vị trí, phân khúc giá và đặc điểm thiết kế
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {similarListings.map((simItem) => (
              <ListingCard key={simItem.id} listing={simItem} />
            ))}
          </div>
        </section>
      )}

      {/* Inquiry Modal */}
      <InquiryModal
        listingId={listing.id}
        listingTitle={listing.title}
        isOpen={inquiryModalOpen}
        onClose={() => setInquiryModalOpen(false)}
      />
    </div>
  );
};
