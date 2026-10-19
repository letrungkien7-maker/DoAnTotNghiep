import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Heart, MapPin, BedDouble, Bath, Eye, Calendar, ShieldCheck } from 'lucide-react';
import { ListingCard as ListingCardType } from '@/types';
import { formatDate, formatPrice, formatPricePerMeter, getStatusBadge } from '@/utils/formatters';
import { interactionService } from '@/services/interaction.service';
import { useAuth } from '@/context/AuthContext';

interface ListingCardProps {
  listing: ListingCardType;
  showStatus?: boolean;
  onFavoriteChange?: (listingId: number, isFavorited: boolean) => void;
  initialFavorited?: boolean;
}

export const ListingCard: React.FC<ListingCardProps> = ({
  listing,
  showStatus = false,
  onFavoriteChange,
  initialFavorited = false,
}) => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [isFavorited, setIsFavorited] = useState<boolean>(initialFavorited);
  const [loadingFav, setLoadingFav] = useState<boolean>(false);

  const fallbackImage =
    'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&auto=format&fit=crop&q=80';

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    setLoadingFav(true);
    try {
      const res = await interactionService.toggleFavorite(listing.id);
      setIsFavorited(res.is_favorited);
      if (onFavoriteChange) {
        onFavoriteChange(listing.id, res.is_favorited);
      }
    } catch {
      // Failed silently or handle
    } finally {
      setLoadingFav(false);
    }
  };

  const statusBadge = getStatusBadge(listing.status);

  return (
    <div className="group bg-white rounded-xl border border-gray-200 overflow-hidden shadow-xs hover:shadow-md transition-all duration-200 flex flex-col">
      {/* Thumbnail area */}
      <div className="relative aspect-[16/10] bg-gray-100 overflow-hidden">
        <Link to={`/listings/${listing.id}`}>
          <img
            src={listing.thumbnail_url || fallbackImage}
            alt={listing.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              (e.target as HTMLImageElement).src = fallbackImage;
            }}
          />
        </Link>

        {/* Transaction Type Tag */}
        <span
          className={`absolute top-3 left-3 text-xs font-semibold px-2.5 py-1 rounded-md shadow-xs ${
            listing.transaction_type === 'SALE'
              ? 'bg-blue-600 text-white'
              : 'bg-emerald-600 text-white'
          }`}
        >
          {listing.transaction_type === 'SALE' ? 'Bán' : 'Cho thuê'}
        </span>

        {/* Status Badge if required */}
        {showStatus && (
          <span
            className={`absolute top-3 left-16 text-xs font-semibold px-2.5 py-1 rounded-md border ${statusBadge.bg} ${statusBadge.text}`}
          >
            {statusBadge.label}
          </span>
        )}

        {/* Favorite Button */}
        <button
          onClick={handleFavoriteClick}
          disabled={loadingFav}
          className="absolute top-3 right-3 p-2 rounded-full bg-white/90 hover:bg-white text-gray-700 hover:text-red-500 shadow-md transition"
          title={isFavorited ? 'Bỏ lưu tin' : 'Lưu tin'}
        >
          <Heart
            className={`w-4 h-4 transition ${
              isFavorited ? 'fill-red-500 text-red-500' : 'text-gray-600'
            }`}
          />
        </button>

        {/* Price & Area Overlay Bar */}
        <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-3 text-white flex items-end justify-between">
          <div>
            <div className="text-lg font-bold text-amber-300 drop-shadow-xs leading-none">
              {formatPrice(listing.price, listing.price_unit, listing.transaction_type)}
            </div>
            {listing.area > 0 && (
              <div className="text-[11px] text-gray-300 font-medium mt-1">
                {formatPricePerMeter(listing.price, listing.area, listing.transaction_type)}
              </div>
            )}
          </div>
          <div className="text-xs font-semibold bg-white/20 border border-white/20 px-2.5 py-0.5 rounded-md backdrop-blur-md">
            {listing.area} m²
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between gap-2">
            <span className="text-[11px] font-bold text-blue-600 uppercase tracking-wide">
              {listing.category_name}
            </span>
            <span className="inline-flex items-center space-x-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded-md border border-emerald-200">
              <ShieldCheck className="w-3 h-3 text-emerald-600" />
              <span>Sổ đỏ/hồng</span>
            </span>
          </div>

          <Link to={`/listings/${listing.id}`}>
            <h3 className="font-semibold text-gray-900 text-sm line-clamp-2 mt-1.5 hover:text-blue-600 transition leading-snug">
              {listing.title}
            </h3>
          </Link>

          <div className="flex items-center text-xs text-gray-500 mt-2 space-x-1">
            <MapPin className="w-3.5 h-3.5 shrink-0 text-gray-400" />
            <span className="truncate">
              {listing.district ? `${listing.district}, ` : ''}{listing.province}
            </span>
          </div>
        </div>

        {/* Specs & Meta */}
        <div className="pt-3 mt-3 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-3">
            {listing.bedrooms !== null && listing.bedrooms !== undefined && listing.bedrooms > 0 && (
              <span className="flex items-center space-x-1" title={`${listing.bedrooms} phòng ngủ`}>
                <BedDouble className="w-3.5 h-3.5 text-gray-400" />
                <span>{listing.bedrooms} PN</span>
              </span>
            )}
            {listing.bathrooms !== null && listing.bathrooms !== undefined && listing.bathrooms > 0 && (
              <span className="flex items-center space-x-1" title={`${listing.bathrooms} phòng tắm/WC`}>
                <Bath className="w-3.5 h-3.5 text-gray-400" />
                <span>{listing.bathrooms} WC</span>
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2 text-[11px]">
            <span className="flex items-center space-x-1" title="Lượt xem">
              <Eye className="w-3 h-3 text-gray-400" />
              <span>{listing.view_count}</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <Calendar className="w-3 h-3 text-gray-400" />
              <span>{formatDate(listing.published_at || listing.created_at)}</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
