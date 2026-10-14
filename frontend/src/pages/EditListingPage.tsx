import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Building2,
  Trash2,
  Image as ImageIcon,
  AlertCircle,
  Loader2,
  Check,
  Lock,
  ArrowLeft,
} from 'lucide-react';
import { Category, ListingDetail, ListingImage } from '@/types';
import { categoryService } from '@/services/category.service';
import { listingService } from '@/services/listing.service';
import { getErrorMessage } from '@/services/api';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

export const EditListingPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [categories, setCategories] = useState<Category[]>([]);
  const [initialLoading, setInitialLoading] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [listing, setListing] = useState<ListingDetail | null>(null);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState<number | ''>('');
  const [transactionType, setTransactionType] = useState<'SALE' | 'RENT'>('SALE');
  const [price, setPrice] = useState<string>('');
  const [priceUnit, setPriceUnit] = useState<string>('TOTAL');
  const [area, setArea] = useState<string>('');
  const [bedrooms, setBedrooms] = useState<string>('');
  const [bathrooms, setBathrooms] = useState<string>('');
  const [direction, setDirection] = useState<string>('');
  const [legalStatus, setLegalStatus] = useState<string>('');
  const [addressText, setAddressText] = useState('');
  const [province, setProvince] = useState('');
  const [district, setDistrict] = useState('');
  const [ward, setWard] = useState('');
  const [features, setFeatures] = useState<string[]>([]);
  const [newFeature, setNewFeature] = useState('');
  const [images, setImages] = useState<ListingImage[]>([]);
  const [imageUrlInput, setImageUrlInput] = useState('');

  useEffect(() => {
    if (!id) return;
    const loadData = async () => {
      setInitialLoading(true);
      try {
        const [cats, detail] = await Promise.all([
          categoryService.getCategories(),
          listingService.getListingDetail(Number(id)),
        ]);
        setCategories(cats);
        setListing(detail);

        setTitle(detail.title);
        setDescription(detail.description);
        setCategoryId(detail.category_id);
        setTransactionType(detail.transaction_type);
        setPrice(String(detail.price));
        setPriceUnit(detail.price_unit);
        setArea(String(detail.area));
        setBedrooms(detail.bedrooms !== null ? String(detail.bedrooms) : '');
        setBathrooms(detail.bathrooms !== null ? String(detail.bathrooms) : '');
        setDirection(detail.direction || '');
        setLegalStatus(detail.legal_status || '');
        setAddressText(detail.address_text);
        setProvince(detail.province);
        setDistrict(detail.district);
        setWard(detail.ward || '');
        setFeatures(detail.features || []);
        setImages(detail.images || []);
      } catch (err) {
        setError(getErrorMessage(err, 'Không thể tải thông tin tin đăng'));
      } finally {
        setInitialLoading(false);
      }
    };
    loadData();
  }, [id]);

  const handleAddFeature = () => {
    if (newFeature.trim() && !features.includes(newFeature.trim())) {
      setFeatures([...features, newFeature.trim()]);
      setNewFeature('');
    }
  };

  const handleRemoveFeature = (feat: string) => {
    setFeatures(features.filter((f) => f !== feat));
  };

  const handleAddImage = () => {
    if (!imageUrlInput.trim()) return;
    const newImg: ListingImage = {
      image_url: imageUrlInput.trim(),
      public_id: `img_${Date.now()}`,
      is_thumbnail: images.length === 0,
      display_order: images.length,
    };
    setImages([...images, newImg]);
    setImageUrlInput('');
  };

  const handleRemoveImage = (index: number) => {
    const updated = images.filter((_, i) => i !== index);
    if (updated.length > 0 && !updated.some((img) => img.is_thumbnail)) {
      updated[0].is_thumbnail = true;
    }
    setImages(updated);
  };

  const handleSetThumbnail = (index: number) => {
    setImages(
      images.map((img, i) => ({
        ...img,
        is_thumbnail: i === index,
      }))
    );
  };

  const handleSubmit = async (submitForApproval: boolean) => {
    if (!id) return;
    setError(null);

    if (!title.trim() || title.length < 20) {
      setError('Tiêu đề phải từ 20 đến 200 ký tự.');
      return;
    }
    if (!description.trim() || description.length < 50) {
      setError('Mô tả phải từ 50 đến 3000 ký tự.');
      return;
    }
    if (submitForApproval && images.length < 3) {
      setError('Nộp duyệt yêu cầu tối thiểu 3 hình ảnh minh họa.');
      return;
    }

    setLoading(true);
    try {
      await listingService.updateListing(Number(id), {
        title: title.trim(),
        description: description.trim(),
        category_id: Number(categoryId),
        transaction_type: transactionType,
        price: Number(price),
        price_unit: priceUnit,
        area: Number(area),
        bedrooms: bedrooms ? Number(bedrooms) : undefined,
        bathrooms: bathrooms ? Number(bathrooms) : undefined,
        direction: direction || undefined,
        legal_status: legalStatus || undefined,
        address_text: addressText.trim(),
        province,
        district,
        ward,
        features,
        images,
        submit_for_approval: submitForApproval,
      });
      navigate('/my-listings');
    } catch (err) {
      setError(getErrorMessage(err, 'Không thể cập nhật tin đăng.'));
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="max-w-4xl mx-auto py-16">
        <LoadingSpinner message="Đang tải dữ liệu tin đăng..." />
      </div>
    );
  }

  if (!listing) return null;

  const isLocked = listing.status === 'PENDING_APPROVAL';

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center space-x-2 text-xs text-gray-500">
        <button
          onClick={() => navigate('/my-listings')}
          className="flex items-center space-x-1 hover:text-blue-600 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Quay lại Quản lý tin đăng</span>
        </button>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Chỉnh sửa tin đăng #{listing.id}</h1>
          <p className="text-xs text-gray-500 mt-0.5">Trạng thái hiện tại: {listing.status}</p>
        </div>
      </div>

      {/* Lock alert for PENDING_APPROVAL status */}
      {isLocked && (
        <div className="p-4 bg-amber-50 border border-amber-300 rounded-2xl flex items-start space-x-3 text-amber-800 text-xs leading-relaxed">
          <Lock className="w-5 h-5 shrink-0 text-amber-600 mt-0.5" />
          <div>
            <strong className="font-bold block text-sm">Tin đăng đang chờ Admin kiểm duyệt!</strong>
            Tin đang trong hàng đợi phê duyệt của hệ thống. Bạn không thể thay đổi thông tin trong thời gian này để đảm bảo tính minh bạch.
          </div>
        </div>
      )}

      {listing.status === 'REJECTED' && listing.rejection_reason && (
        <div className="p-4 bg-red-50 border border-red-300 rounded-2xl flex items-start space-x-3 text-red-800 text-xs">
          <AlertCircle className="w-5 h-5 shrink-0 text-red-600 mt-0.5" />
          <div>
            <strong className="font-bold block text-sm">Lý do từ chối từ Ban quản trị:</strong>
            {listing.rejection_reason}
            <p className="mt-1 text-[11px] text-red-600">
              Vui lòng bổ sung hoặc sửa đổi theo yêu cầu ở trên, sau đó nhấn "Nộp duyệt lại".
            </p>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      <fieldset disabled={isLocked} className="space-y-6">
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-xs space-y-6 text-xs">
          {/* Section 1 */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-gray-900 pb-2 border-b border-gray-100 flex items-center space-x-2">
              <Building2 className="w-4 h-4 text-blue-600" />
              <span>1. Phân loại & Hình thức giao dịch</span>
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">Hình thức</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setTransactionType('SALE')}
                    className={`py-2 text-center rounded-xl font-bold transition ${
                      transactionType === 'SALE'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Bán
                  </button>
                  <button
                    type="button"
                    onClick={() => setTransactionType('RENT')}
                    className={`py-2 text-center rounded-xl font-bold transition ${
                      transactionType === 'RENT'
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Cho thuê
                  </button>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Loại hình BĐS</label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(Number(e.target.value))}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section 2: Pricing & Specs */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-gray-900 pb-2 border-b border-gray-100">
              2. Mức giá & Kích thước
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block font-semibold text-gray-700 mb-1">Mức giá (VNĐ)</label>
                <input
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Đơn vị tính</label>
                <select
                  value={priceUnit}
                  onChange={(e) => setPriceUnit(e.target.value)}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-xl"
                >
                  <option value="TOTAL">Tổng giá (VNĐ)</option>
                  <option value="MONTH">Tháng (Thuê/tháng)</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-gray-700 mb-1">Diện tích (m²)</label>
                <input
                  type="number"
                  value={area}
                  onChange={(e) => setArea(e.target.value)}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-xl"
                />
              </div>
            </div>
          </div>

          {/* Section 3: Content */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-gray-900 pb-2 border-b border-gray-100">
              3. Tiêu đề & Nội dung
            </h2>
            <div>
              <label className="block font-semibold text-gray-700 mb-1">Tiêu đề tin</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl"
              />
            </div>
            <div>
              <label className="block font-semibold text-gray-700 mb-1">Mô tả chi tiết</label>
              <textarea
                rows={5}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl resize-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1.5">Tiện ích kèm theo</label>
              <div className="flex gap-2 mb-2">
                <input
                  type="text"
                  value={newFeature}
                  onChange={(e) => setNewFeature(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddFeature())}
                  placeholder="Thêm tiện ích..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-xl"
                />
                <button
                  type="button"
                  onClick={handleAddFeature}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl"
                >
                  Thêm
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {features.map((f, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg border border-blue-200 flex items-center space-x-1"
                  >
                    <span>{f}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveFeature(f)}
                      className="text-blue-400 hover:text-red-500"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Section 4: Images */}
          <div className="space-y-4">
            <h2 className="text-sm font-bold text-gray-900 pb-2 border-b border-gray-100 flex items-center space-x-2">
              <ImageIcon className="w-4 h-4 text-blue-600" />
              <span>4. Hình ảnh ({images.length}/10)</span>
            </h2>

            <div className="flex gap-2">
              <input
                type="url"
                value={imageUrlInput}
                onChange={(e) => setImageUrlInput(e.target.value)}
                placeholder="https://..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-xl"
              />
              <button
                type="button"
                onClick={handleAddImage}
                className="px-4 py-2 bg-blue-600 text-white rounded-xl"
              >
                Thêm ảnh
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {images.map((img, idx) => (
                <div
                  key={idx}
                  className={`relative rounded-xl overflow-hidden border-2 aspect-[4/3] group ${
                    img.is_thumbnail ? 'border-blue-600 ring-2 ring-blue-200' : 'border-gray-200'
                  }`}
                >
                  <img src={img.image_url} alt="Preview" className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-2">
                    {!img.is_thumbnail && (
                      <button
                        type="button"
                        onClick={() => handleSetThumbnail(idx)}
                        className="p-1 bg-blue-600 text-white rounded text-[10px]"
                      >
                        Đại diện
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(idx)}
                      className="p-1 bg-red-600 text-white rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          {!isLocked && (
            <div className="pt-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                type="button"
                disabled={loading}
                onClick={() => handleSubmit(false)}
                className="px-6 py-2.5 border border-gray-300 font-semibold rounded-xl hover:bg-gray-50"
              >
                Lưu cập nhật
              </button>

              {(listing.status === 'DRAFT' || listing.status === 'REJECTED') && (
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handleSubmit(true)}
                  className="px-8 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition flex items-center space-x-1.5 shadow-md"
                >
                  {loading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Check className="w-4 h-4" />
                  )}
                  <span>Nộp duyệt lại tin này</span>
                </button>
              )}
            </div>
          )}
        </div>
      </fieldset>
    </div>
  );
};
