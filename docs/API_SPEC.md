# ĐẶC TẢ REST API (API SPECIFICATION)

Base URL: `http://127.0.0.1:8000/api/v1`

---

## 1. Chuẩn Hóa Phản Hồi (Standard Response Envelope)

### 1.1. Phản hồi Thành Công (200, 201)
```json
{
  "success": true,
  "data": { ... },
  "message": "Thao tác thành công"
}
```

### 1.2. Phản hồi Lỗi Chuẩn Hóa (400, 401, 403, 404, 409, 422, 429, 500)
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Email hoặc mật khẩu không chính xác",
    "details": null
  },
  "timestamp": "2026-10-14T13:30:00Z"
}
```

### 1.3. Bảng Mã Lỗi Nghiệp Vụ
| HTTP Status | Mã lỗi (`code`) | Ý nghĩa nghiệp vụ |
| :---: | :--- | :--- |
| `400` | `LISTING_LOCKED_PENDING` | Tin đăng đang ở trạng thái chờ duyệt (PENDING_APPROVAL), chủ tin không được sửa trực tiếp |
| `400` | `SELF_INQUIRY_NOT_ALLOWED` | Người bán không thể tự gửi form yêu cầu tư vấn cho chính tin đăng của mình |
| `401` | `INVALID_CREDENTIALS` | Sai thông tin đăng nhập hoặc thiếu Bearer token hợp lệ |
| `401` | `TOKEN_EXPIRED` | Token JWT đã hết thời gian hiệu lực |
| `403` | `FORBIDDEN_RESOURCE` | Người dùng thường cố tình gọi API Admin hoặc can thiệp tin của người khác |
| `403` | `USER_INACTIVE` | Tài khoản đã bị khóa bởi quản trị viên |
| `404` | `RECORD_NOT_FOUND` | Không tìm thấy người dùng, danh mục hoặc tin đăng |
| `409` | `RESOURCE_CONFLICT` | Trùng lặp dữ liệu độc bản (Email, Tên hoặc Slug danh mục) |
| `422` | `VALIDATION_FAILED` | Lỗi validate dữ liệu (thiếu 3 ảnh khi nộp duyệt, giá <= 0, v.v.) |
| `429` | `RATE_LIMIT_EXCEEDED` | Quá số lượt đăng nhập cho phép (hạn chế brute-force) |
| `500` | `INTERNAL_SERVER_ERROR` | Lỗi máy chủ (che giấu stack trace để đảm bảo bảo mật) |

---

## 2. Phân Hệ Xác Thực & Tài Khoản (Auth & Profile)

| Method | Endpoint | Quyền | Mô tả |
| :--- | :--- | :---: | :--- |
| `POST` | `/auth/register` | Public | Đăng ký tài khoản mới (mặc định gán role `USER`) |
| `POST` | `/auth/login` | Public | Đăng nhập nhận JWT Token (có bảo vệ Rate Limit) |
| `POST` | `/auth/logout` | User | Đăng xuất tài khoản |
| `GET` | `/users/me` | User | Lấy thông tin hồ sơ của tài khoản đang đăng nhập |
| `PUT` | `/users/me` | User | Cập nhật họ tên, số điện thoại, avatar cá nhân |
| `GET` | `/users` | Admin | Tìm kiếm, lọc và phân trang danh sách tài khoản |
| `PATCH` | `/users/{id}/status` | Admin | Khóa hoặc kích hoạt lại tài khoản người dùng |

---

## 3. Phân Hệ Danh Mục Bất Động Sản (Categories)

### 3.1. Danh Sách Danh Mục
- **Endpoint:** `GET /api/v1/categories`
- **Quyền:** Public
- **Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Căn hộ chung cư",
      "slug": "can-ho-chung-cu",
      "description": "Căn hộ cao cấp, trung cấp và nhà ở xã hội"
    }
  ],
  "message": "Lấy danh mục thành công"
}
```

### 3.2. Tạo Danh Mục Mới
- **Endpoint:** `POST /api/v1/categories`
- **Quyền:** ADMIN Only
- **Request Body:**
```json
{
  "name": "Biệt thự nghỉ dưỡng",
  "slug": "biet-thu-nghi-duong",
  "description": "Biệt thự biển và ven đồi"
}
```

---

## 4. Phân Hệ Bất Động Sản (Listings)

### 4.1. Tìm Kiếm & Lọc BĐS Công Khai
- **Endpoint:** `GET /api/v1/listings`
- **Quyền:** Public (chỉ trả về tin `APPROVED` và `expired_at > now()`)
- **Query Params:**
  - `keyword`: Tìm kiếm theo từ khóa trong tiêu đề, mô tả, địa chỉ
  - `category_id`: Lọc theo ID loại hình BĐS
  - `transaction_type`: `SALE` (Bán) hoặc `RENT` (Cho thuê)
  - `min_price`, `max_price`: Khoảng giá tìm kiếm
  - `min_area`, `max_area`: Khoảng diện tích ($m^2$)
  - `province`, `district`: Lọc theo tỉnh/thành, quận/huyện
  - `bedrooms`: Số phòng ngủ tối thiểu
  - `sort_by`: `newest` (mặc định), `price_asc`, `price_desc`, `area_asc`, `area_desc`
  - `page` (default 1), `size` (default 12, max 50)
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "Bán căn hộ 2PN Vinhomes Smart City full nội thất cao cấp",
        "price": 3200000000.0,
        "price_unit": "TOTAL",
        "area": 65.0,
        "bedrooms": 2,
        "bathrooms": 2,
        "address_text": "Đại lộ Thăng Long, Phường Tây Mỗ",
        "province": "Hà Nội",
        "district": "Nam Từ Liêm",
        "transaction_type": "SALE",
        "category_id": 1,
        "category_name": "Căn hộ chung cư",
        "thumbnail_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800",
        "status": "APPROVED",
        "view_count": 45,
        "published_at": "2026-10-12T13:30:00Z",
        "created_at": "2026-10-12T13:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 12,
    "total_pages": 1
  },
  "message": "Tìm kiếm bất động sản thành công"
}
```

---

### 4.2. Xem Chi Tiết Bất Động Sản
- **Endpoint:** `GET /api/v1/listings/{id}`
- **Quyền:** Public
- **Headers:** `X-Session-Id` (optional, dùng để ghi nhận lịch sử xem)
- **Quy tắc bảo mật & riêng tư (BR-05):**
  - Khách vãng lai: Số điện thoại người bán được che dạng `0912.xxx.xxx`.
  - Người dùng đã đăng nhập (kèm Bearer Token): Hiển thị đầy đủ số điện thoại `0912345678`.
  - Tự động tăng `view_count` và ghi log vào `user_view_history`.
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 2,
    "title": "Bán căn hộ 2PN Vinhomes Smart City full nội thất cao cấp",
    "description": "Căn hộ tầng trung view công viên trung tâm cực đẹp...",
    "category_id": 1,
    "category_name": "Căn hộ chung cư",
    "transaction_type": "SALE",
    "price": 3200000000.0,
    "price_unit": "TOTAL",
    "area": 65.0,
    "bedrooms": 2,
    "bathrooms": 2,
    "direction": "Đông Nam",
    "legal_status": "Sổ hồng lâu dài",
    "address_text": "Đại lộ Thăng Long, Phường Tây Mỗ",
    "province": "Hà Nội",
    "district": "Nam Từ Liêm",
    "ward": "Phường Tây Mỗ",
    "latitude": 21.0068,
    "longitude": 105.7441,
    "status": "APPROVED",
    "rejection_reason": null,
    "view_count": 46,
    "published_at": "2026-10-12T13:30:00Z",
    "expired_at": "2026-11-11T13:30:00Z",
    "images": [
      {
        "id": 1,
        "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800",
        "public_id": "demo_apt_1",
        "is_thumbnail": true,
        "display_order": 0
      }
    ],
    "features": ["Sổ hồng chính chủ", "Nội thất đầy đủ", "Bể bơi 4 mùa"],
    "owner_id": 2,
    "owner_name": "Nguyễn Văn Minh",
    "owner_phone": "0912345678",
    "owner_avatar": null,
    "is_favorite": false
  },
  "message": "Lấy chi tiết tin đăng thành công"
}
```

---

### 4.3. Đăng Tin Mới
- **Endpoint:** `POST /api/v1/listings`
- **Quyền:** Authenticated User
- **Quy tắc kiểm tra:**
  - `is_draft = True`: Lưu nháp, không bắt buộc số lượng ảnh.
  - `is_draft = False`: Gửi duyệt (`PENDING_APPROVAL`), bắt buộc tối thiểu 3 ảnh và tối đa 10 ảnh (định dạng JPG, JPEG, PNG, WEBP).
- **Request Body:**
```json
{
  "title": "Bán nhà liền kề KĐT Geleximco Lê Trọng Tấn 100m2",
  "description": "Nhà xây thô hoàn thiện mặt ngoài 4 tầng hiện đại, đường trước nhà 13.5m có vỉa hè rộng rãi.",
  "category_id": 2,
  "transaction_type": "SALE",
  "price": 8500000000.0,
  "price_unit": "TOTAL",
  "area": 100.0,
  "bedrooms": 4,
  "bathrooms": 4,
  "direction": "Đông Nam",
  "legal_status": "Sổ đỏ chính chủ",
  "address_text": "Khu D Geleximco Lê Trọng Tấn",
  "province": "Hà Nội",
  "district": "Hà Đông",
  "features": ["Gara ô tô", "Đường 13m"],
  "images": [
    { "image_url": "https://cloudinary.com/front.jpg", "public_id": "p1", "is_thumbnail": true },
    { "image_url": "https://cloudinary.com/living.jpg", "public_id": "p2" },
    { "image_url": "https://cloudinary.com/bedroom.jpg", "public_id": "p3" }
  ],
  "is_draft": false
}
```

---

### 4.4. Chỉnh Sửa & Quản Lý Tin Của Tôi
| Method | Endpoint | Quyền | Mô tả |
| :--- | :--- | :---: | :--- |
| `GET` | `/listings/my/all` | User | Xem toàn bộ tin của cá nhân kèm đủ mọi trạng thái (Draft, Pending, Approved, v.v.) |
| `PUT` | `/listings/{id}` | Owner | Chỉnh sửa tin của tôi (bị khóa nếu tin đang ở trạng thái `PENDING_APPROVAL`) |
| `DELETE` | `/listings/{id}` | Owner/Admin | Xóa tin đăng khỏi hệ thống |
| `PATCH` | `/listings/{id}/visibility` | Owner | Ẩn (`is_hidden: true`) hoặc hiện lại (`is_hidden: false`) tin đã duyệt |
| `POST` | `/listings/{id}/renew` | Owner | Gia hạn tin đã hết hạn thêm 30 ngày |

---

## 5. Phân Hệ Kiểm Duyệt Quản Trị (Admin Moderation)

### 5.1. Danh Sách Tin Chờ Duyệt
- **Endpoint:** `GET /api/v1/admin/listings/pending`
- **Quyền:** ADMIN Only
- **Query Params:** `page` (default 1), `size` (default 10)

### 5.2. Phê Duyệt hoặc Từ Chối Tin
- **Endpoint:** `PATCH /api/v1/admin/listings/{id}/moderate`
- **Quyền:** ADMIN Only
- **Phê duyệt:**
```json
{
  "action": "APPROVE"
}
```
*(Chuyển status sang `APPROVED`, đặt `published_at = now()` và `expired_at = now() + 30 days`).*

- **Từ chối:**
```json
{
  "action": "REJECT",
  "rejection_reason": "Ảnh không rõ nét, thiếu thông tin giấy tờ pháp lý."
}
```
*(Chuyển status sang `REJECTED`, lưu lý do từ chối để chủ tin sửa lại).*

---

## 6. Phân Hệ Tương Tác & Tư Vấn (Interactions)

### 6.1. Yêu Thích Bất Động Sản (Favorites)
- **`POST /api/v1/favorites/{listing_id}`** (User): Bấm lần đầu là thêm vào yêu thích (`is_favorited: true`), bấm lần sau là hủy yêu thích (`is_favorited: false`).
- **`GET /api/v1/favorites`** (User): Danh sách các tin BĐS mà người dùng đã lưu yêu thích.

### 6.2. Yêu Cầu Tư Vấn / Liên Hệ (Inquiries)
- **`POST /api/v1/inquiries`** (Public/User): Gửi yêu cầu tư vấn cho người đăng BĐS.
  - Chặn người bán tự gửi yêu cầu cho chính tin của mình (`SELF_INQUIRY_NOT_ALLOWED`).
- **`GET /api/v1/inquiries/received`** (Owner): Người đăng xem danh sách khách hàng gửi yêu cầu tư vấn.
- **`PATCH /api/v1/inquiries/{id}/status`** (Owner): Người đăng đánh dấu trạng thái (`CONTACTED` hoặc `CLOSED`).

---

---

## 7. Phân Hệ Gợi Ý Bất Động Sản Thông Minh (Recommendations)

### 7.1. Gợi Ý Đa Tiêu Chí (Content-Based Multi-Criteria Scoring)
- **Endpoint:** `POST /api/v1/recommendations/search`
- **Quyền:** Public / User (Hỗ trợ cá nhân hóa kết hợp nếu có Bearer token)
- **Mục đích:** Dùng chung cho giao diện Web và Chatbot AI Assistant.
- **Request Body:**
```json
{
  "transaction_type": "SALE",
  "category_id": 1,
  "province": "Hà Nội",
  "district": "Nam Từ Liêm",
  "budget_min": 3000000000.0,
  "budget_max": 4000000000.0,
  "bedrooms": 2,
  "features": ["Nội thất đầy đủ", "Sổ đỏ chính chủ"],
  "top_k": 5
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "title": "Bán căn hộ 2PN Vinhomes Smart City full nội thất cao cấp",
        "price": 3200000000.0,
        "price_unit": "TOTAL",
        "area": 65.0,
        "bedrooms": 2,
        "bathrooms": 2,
        "address_text": "Đại lộ Thăng Long, Phường Tây Mỗ",
        "province": "Hà Nội",
        "district": "Nam Từ Liêm",
        "transaction_type": "SALE",
        "category_id": 1,
        "category_name": "Căn hộ chung cư",
        "thumbnail_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800",
        "status": "APPROVED",
        "view_count": 45,
        "match_score": 0.95,
        "match_percentage": 95.0,
        "score_breakdown": {
          "price_score": 1.0,
          "location_score": 1.0,
          "category_score": 1.0,
          "area_score": 0.95,
          "bedroom_score": 1.0,
          "feature_score": 1.0,
          "total_score": 0.95,
          "match_percentage": 95.0
        },
        "match_reasons": [
          "Vị trí đúng trọng tâm tại Nam Từ Liêm, Hà Nội",
          "Mức giá nằm trọn vẹn trong khoảng ngân sách dự kiến của bạn",
          "Khớp chính xác loại hình: Căn hộ chung cư",
          "Đáp ứng đủ 2 phòng ngủ theo tiêu chuẩn",
          "Trùng khớp tiện ích: Nội thất đầy đủ, Sổ đỏ chính chủ"
        ]
      }
    ],
    "total": 1,
    "strategy": "CONTENT_BASED_SCORING",
    "user_profile_applied": false
  },
  "message": "Gợi ý bất động sản thành công"
}
```

### 7.2. Bảng Tin Cá Nhân Hóa (Personalized Behavioral Feed)
- **Endpoint:** `GET /api/v1/recommendations/personalized?limit=10`
- **Quyền:** Public / User (kèm Bearer Token hoặc Header `X-Session-Id`)
- **Chiến lược:**
  - Nếu người dùng đã có lịch sử xem hoặc lưu tin: Suy diễn hồ sơ hành vi (giá trung bình, loại hình và quận hay xem nhất) -> Trả về danh sách được cá nhân hóa (`strategy: PERSONALIZED_BEHAVIORAL_FEED`).
  - Nếu người dùng mới chưa có dữ liệu (Cold Start): Tự động trả về tin đăng thịnh hành nhất (`strategy: POPULAR_COLD_START`).

### 7.3. Bất Động Sản Tương Tự (Item-to-Item Similarity)
- **Endpoint:** `GET /api/v1/recommendations/similar/{listing_id}?limit=4`
- **Quyền:** Public
- **Chiến lược:** Tính độ tương đồng vector Cosine giữa tin đang xem với toàn bộ tin khác cùng phân khúc.

---

## 8. Khởi Tạo Dữ Liệu Mẫu (Seed Data)

Script khởi tạo sẵn 5 danh mục BĐS chuẩn, 4 tài khoản mẫu (Admin, 2 Chủ tin, 1 Khách xem), các tin đăng đa trạng thái kèm ảnh và tiện ích:

```powershell
# Chạy script tại thư mục backend:
cd backend
.\.venv\Scripts\Activate.ps1
python scripts/seed_data.py
```

### Tài khoản Demo có sẵn sau khi Seed:
| Email | Mật khẩu | Quyền | Họ tên | Vai trò demo |
| :--- | :--- | :---: | :--- | :--- |
| `admin@bds.vn` | `AdminPass123!` | `ADMIN` | Quản Trị Viên Hệ Thống | Kiểm duyệt tin, quản lý tài khoản |
| `chutin1@bds.vn` | `Password123!` | `USER` | Nguyễn Văn Minh | Đăng tin căn hộ, tiếp nhận liên hệ |
| `chutin2@bds.vn` | `Password123!` | `USER` | Lê Hoàng Nam | Đăng tin nhà phố, đất nền |
| `khachxem@bds.vn` | `Password123!` | `USER` | Trần Thu Trang | Khách tìm kiếm, lưu yêu thích, gửi tư vấn |

