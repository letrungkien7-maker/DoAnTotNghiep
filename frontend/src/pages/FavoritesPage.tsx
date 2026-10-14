import React, { useEffect, useState } from 'react';
import { Heart } from 'lucide-react';
import { ListingCard as ListingCardType } from '@/types';
import { interactionService } from '@/services/interaction.service';
import { ListingCard } from '@/components/listings/ListingCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { EmptyState } from '@/components/common/EmptyState';

export const FavoritesPage: React.FC = () => {
  const [favorites, setFavorites] = useState<ListingCardType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchFavorites = async () => {
    setLoading(true);
    try {
      const data = await interactionService.getFavorites();
      setFavorites(data);
    } catch {
      setFavorites([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFavorites();
  }, []);

  const handleFavoriteChange = (listingId: number, isFavorited: boolean) => {
    if (!isFavorited) {
      setFavorites((prev) => prev.filter((item) => item.id !== listingId));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center space-x-2">
        <div className="p-2 bg-red-50 text-red-600 rounded-xl">
          <Heart className="w-5 h-5 fill-red-500" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Danh sách tin đã lưu</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Các bất động sản bạn đang quan tâm và theo dõi
          </p>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Đang tải danh sách tin yêu thích..." />
      ) : favorites.length === 0 ? (
        <EmptyState
          icon={<Heart className="w-10 h-10 text-red-400" />}
          title="Chưa có bất động sản nào được lưu"
          description="Bấm vào biểu tượng trái tim ở bất kỳ tin đăng nào để lưu lại và xem lại tại đây."
          actionText="Khám phá bất động sản ngay"
          actionLink="/search"
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {favorites.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              initialFavorited={true}
              onFavoriteChange={handleFavoriteChange}
            />
          ))}
        </div>
      )}
    </div>
  );
};
