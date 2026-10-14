import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  Plus,
  Trash2,
  Image as ImageIcon,
  AlertCircle,
  Loader2,
  Check,
  Sparkles,
} from 'lucide-react';
import { Category, ListingCreatePayload, ListingImage, TransactionType } from '@/types';
import { categoryService } from '@/services/category.service';
import { listingService } from '@/services/listing.service';
import { getErrorMessage } from '@/services/api';

export const PostListingPage: React.FC = () => {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState<number | ''>('');
  const [transactionType, setTransactionType] = useState<TransactionType>('SALE');
  const [price, setPrice] = useState<string>('');
  const [priceUnit, setPriceUnit] = useState<string>('TOTAL');
  const [area, setArea] = useState<string>('');
  const [bedrooms, setBedrooms] = useState<string>('');
  const [bathrooms, setBathrooms] = useState<string>('');
  const [direction, setDirection] = useState<string>('Đông Nam');
  const [legalStatus, setLegalStatus] = useState<string>('Sổ đỏ / Sổ hồng chính chủ');

  const [addressText, setAddressText] = useState('');
  const [province, setProvince] = useState('Hà Nội');
  const [district, setDistrict] = useState('Cầu Giấy');
  const [ward, setWard] = useState('Dịch Vọng');

  // Amenities
  const [features, setFeatures] = useState<string[]>([
    'Sổ đỏ chính chủ',
    'Nội thất đầy đủ',
    'Thang máy',
  ]);
  const [newFeature, setNewFeature] = useState('');

  // Images
  const [images, setImages] = useState<ListingImage[]>([]);
  const [imageUrlInput, setImageUrlInput] = useState('');

  useEffect(() => {
    categoryService.getCategories().then((data) => {
      setCategories(data);
      if (data.length > 0) setCategoryId(data[0].id);
    });
  }, []);

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

  // Quick fill demo sample images
  const handleFillDemoImages = () => {
    setImages([
      {
        image_url: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800',
        public_id: 'demo_img_1',
        is_thumbnail: true,
        display_order: 0,
      },
      {
        image_url: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800',
        public_id: 'demo_img_2',
        is_thumbnail: false,
        display_order: 1,
      },
      {
        image_url: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800',
        public_id: 'demo_img_3',
        is_thumbnail: false,
        display_order: 2,
      },
    ]);
  };

  const handleSubmit = async (isDraft: boolean) => {
    setError(null);

    if (!title.trim() || title.length < 20) {
      setError('Tiêu đề tin đăng phải có độ dài từ 20 đến 200 ký tự.');
      return;
    }
    if (!description.trim() || description.length < 50) {
      setError('Mô tả chi tiết phải có độ dài từ 50 đến 3000 ký tự.');
      return;
    }
    if (!categoryId) {
      setError('Vui lòng chọn loại hình bất động sản.');
      return;
    }
    if (!price || Number(price) <= 0) {
      setError('Mức giá niêm yết phải lớn hơn 0.');
      return;
    }
    if (!area || Number(area) <= 0) {
      setError('Diện tích phải lớn hơn 0 m².');
      return;
    }

    if (!isDraft) {
      if (images.length < 3) {
        setError('Quy tắc kiểm duyệt: Tin gửi duyệt yêu cầu tối thiểu 3 hình ảnh minh họa chất lượng.');
        return;
      }
      if (images.length > 10) {
        setError('Tin đăng cho phép tối đa 10 hình ảnh.');
        return;
      }
    }

    setLoading(true);
    try {
      const payload: ListingCreatePayload = {
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
        address_text: addressText.trim() || `${ward}, ${district}, ${province}`,
        province,
        district,
        ward,
        features,
        images,
        is_draft: isDraft,
      };

      await listingService.createListing(payload);
      navigate('/my-listings');
    } catch (err) {
      setError(getErrorMessage(err, 'Không thể tạo tin đăng. Vui lòng thử lại.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Đăng tin Bất động sản mới</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            Điền đầy đủ thông tin để tin đăng được tiếp cận hàng ngàn khách hàng tiềm năng
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-gray-200 shadow-xs space-y-6 text-xs">
        {/* Section 1: Basic Classification */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-gray-900 pb-2 border-b border-gray-100 flex items-center space-x-2">
            <Building2 className="w-4 h-4 text-blue-600" />
            <span>1. Phân loại & Hình thức giao dịch</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Hình thức giao dịch <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setTransactionType('SALE')}
                  className={`py-2 text-center rounded-xl font-bold transition ${
                    transactionType === 'SALE'
                      ? 'bg-blue-600 text-white shadow-2xs'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Bán bất động sản
                </button>
                <button
                  type="button"
                  onClick={() => setTransactionType('RENT')}
                  className={`py-2 text-center rounded-xl font-bold transition ${
                    transactionType === 'RENT'
                      ? 'bg-emerald-600 text-white shadow-2xs'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Cho thuê
                </button>
              </div>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Loại hình bất động sản <span className="text-red-500">*</span>
              </label>
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
            2. Giá & Thông số kỹ thuật
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Mức giá (VNĐ) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="Ví dụ: 3500000000"
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Đơn vị giá</label>
              <select
                value={priceUnit}
                onChange={(e) => setPriceUnit(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="TOTAL">Tổng giá (VNĐ)</option>
                <option value="MONTH">Tháng (Thuê/tháng)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Diện tích (m²) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={area}
                onChange={(e) => setArea(e.target.value)}
                placeholder="Ví dụ: 75"
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Số phòng ngủ</label>
              <input
                type="number"
                value={bedrooms}
                onChange={(e) => setBedrooms(e.target.value)}
                placeholder="Ví dụ: 2"
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Số phòng tắm/WC</label>
              <input
                type="number"
                value={bathrooms}
                onChange={(e) => setBathrooms(e.target.value)}
                placeholder="Ví dụ: 2"
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Hướng nhà</label>
              <select
                value={direction}
                onChange={(e) => setDirection(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                <option value="Đông">Đông</option>
                <option value="Tây">Tây</option>
                <option value="Nam">Nam</option>
                <option value="Bắc">Bắc</option>
                <option value="Đông Nam">Đông Nam</option>
                <option value="Đông Bắc">Đông Bắc</option>
                <option value="Tây Nam">Tây Nam</option>
                <option value="Tây Bắc">Tây Bắc</option>
              </select>
            </div>

            <div className="sm:col-span-2">
              <label className="block font-semibold text-gray-700 mb-1">Tình trạng pháp lý</label>
              <input
                type="text"
                value={legalStatus}
                onChange={(e) => setLegalStatus(e.target.value)}
                placeholder="Ví dụ: Sổ hồng chính chủ lâu dài"
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Location */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-gray-900 pb-2 border-b border-gray-100">
            3. Địa chỉ bất động sản
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Tỉnh / Thành phố <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={province}
                onChange={(e) => setProvince(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">
                Quận / Huyện <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block font-semibold text-gray-700 mb-1">Phường / Xã</label>
              <input
                type="text"
                value={ward}
                onChange={(e) => setWard(e.target.value)}
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>

            <div className="sm:col-span-3">
              <label className="block font-semibold text-gray-700 mb-1">
                Địa chỉ chi tiết (Đường/Tòa nhà) <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={addressText}
                onChange={(e) => setAddressText(e.target.value)}
                placeholder="Ví dụ: Số 25 Vũ Phạm Hàm, Khu đô thị Trung Hòa"
                className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
              />
            </div>
          </div>
        </div>

        {/* Section 4: Title & Description */}
        <div className="space-y-4">
          <h2 className="text-sm font-bold text-gray-900 pb-2 border-b border-gray-100">
            4. Tiêu đề & Nội dung mô tả
          </h2>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="font-semibold text-gray-700">
                Tiêu đề tin đăng <span className="text-red-500">*</span>
              </label>
              <span className={`text-[10px] ${title.length < 20 ? 'text-amber-600' : 'text-gray-400'}`}>
                {title.length}/200 ký tự (Tối thiểu 20)
              </span>
            </div>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ví dụ: Bán căn hộ 2PN Vinhomes Smart City full nội thất cao cấp view công viên"
              className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="font-semibold text-gray-700">
                Nội dung mô tả chi tiết <span className="text-red-500">*</span>
              </label>
              <span className={`text-[10px] ${description.length < 50 ? 'text-amber-600' : 'text-gray-400'}`}>
                {description.length}/3000 ký tự (Tối thiểu 50)
              </span>
            </div>
            <textarea
              rows={5}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Mô tả cụ thể về vị trí, thiết kế kiến trúc, nội thất bàn giao, tiện ích xung quanh, pháp lý và tiến độ thanh toán..."
              className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none leading-relaxed"
            />
          </div>

          {/* Features */}
          <div>
            <label className="block font-semibold text-gray-700 mb-1.5">Tiện ích kèm theo</label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newFeature}
                onChange={(e) => setNewFeature(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddFeature())}
                placeholder="Nhập tiện ích (Ví dụ: Chỗ để ô tô, Bể bơi, An ninh 24/7) và nhấn Thêm"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
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
                  className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg border border-blue-200 flex items-center space-x-1 font-medium"
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

        {/* Section 5: Image Management */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-gray-100">
            <h2 className="text-sm font-bold text-gray-900 flex items-center space-x-2">
              <ImageIcon className="w-4 h-4 text-blue-600" />
              <span>5. Quản lý hình ảnh ({images.length}/10 ảnh)</span>
            </h2>
            <button
              type="button"
              onClick={handleFillDemoImages}
              className="inline-flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-800 font-semibold"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Chèn nhanh 3 ảnh mẫu để test</span>
            </button>
          </div>

          <div className="flex gap-2">
            <input
              type="url"
              value={imageUrlInput}
              onChange={(e) => setImageUrlInput(e.target.value)}
              placeholder="Nhập liên kết hình ảnh trực tuyến (https://...)..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <button
              type="button"
              onClick={handleAddImage}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl flex items-center space-x-1"
            >
              <Plus className="w-4 h-4" />
              <span>Thêm ảnh</span>
            </button>
          </div>

          {images.length === 0 ? (
            <div className="p-8 text-center bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl">
              <ImageIcon className="w-8 h-8 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500 font-medium">Chưa có hình ảnh nào được thêm.</p>
              <p className="text-[11px] text-gray-400 mt-1">
                Lưu ý: Để nộp duyệt chính thức, tin đăng cần tối thiểu 3 ảnh.
              </p>
            </div>
          ) : (
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
                        className="p-1.5 bg-blue-600 text-white rounded-lg text-[10px] font-bold"
                        title="Đặt làm ảnh đại diện"
                      >
                        Đặt đại diện
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleRemoveImage(idx)}
                      className="p-1.5 bg-red-600 text-white rounded-lg"
                      title="Xóa ảnh"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  {img.is_thumbnail && (
                    <span className="absolute bottom-1 left-1 px-1.5 py-0.5 bg-blue-600 text-white text-[9px] font-bold rounded">
                      Ảnh đại diện
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Action Buttons: Save Draft vs Submit for Review */}
        <div className="pt-6 border-t border-gray-200 flex flex-col sm:flex-row justify-end gap-3">
          <button
            type="button"
            disabled={loading}
            onClick={() => handleSubmit(true)}
            className="px-6 py-2.5 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition"
          >
            Lưu bản nháp (DRAFT)
          </button>

          <button
            type="button"
            disabled={loading}
            onClick={() => handleSubmit(false)}
            className="px-8 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition flex items-center justify-center space-x-2 shadow-md disabled:opacity-50 text-sm"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Đang xử lý...</span>
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                <span>Gửi phê duyệt ngay</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
