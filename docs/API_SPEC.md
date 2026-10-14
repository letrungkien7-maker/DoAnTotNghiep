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
| `401` | `INVALID_CREDENTIALS` | Sai thông tin đăng nhập hoặc thiếu Bearer token hợp lệ |
| `401` | `TOKEN_EXPIRED` | Token JWT đã hết thời gian hiệu lực |
| `403` | `FORBIDDEN_RESOURCE` | Người dùng thường cố tình gọi API yêu cầu quyền ADMIN |
| `403` | `USER_INACTIVE` | Tài khoản đã bị khóa bởi quản trị viên |
| `404` | `RECORD_NOT_FOUND` | Không tìm thấy người dùng hoặc tài nguyên tương ứng |
| `409` | `RESOURCE_CONFLICT` | Trùng lặp dữ liệu độc bản (Email đã được đăng ký) |
| `422` | `VALIDATION_FAILED` | Lỗi định dạng dữ liệu (mật khẩu < 8 ký tự, sai cấu trúc email) |
| `429` | `RATE_LIMIT_EXCEEDED` | Quá số lượt đăng nhập cho phép (hạn chế tấn công brute-force) |
| `500` | `INTERNAL_SERVER_ERROR` | Lỗi máy chủ (che giấu hoàn toàn stack trace để đảm bảo bảo mật) |

---

## 2. Phân Hệ Xác Thực & Tài Khoản (Auth & Profile)

### 2.1. Đăng ký Tài khoản
- **Endpoint:** `POST /api/v1/auth/register`
- **Quyền:** Public
- **Quy tắc bảo mật:** Không nhận trường `role` từ client. Tất cả tài khoản đăng ký mới luôn mặc định là `USER`.
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "Nguyễn Văn A",
  "phone_number": "0912345678"
}
```
- **Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "phone_number": "0912345678",
    "role": "USER",
    "is_active": true,
    "avatar_url": null,
    "created_at": "2026-10-14T13:30:00Z"
  },
  "message": "Đăng ký tài khoản thành công"
}
```

---

### 2.2. Đăng nhập & Lấy Bearer Token
- **Endpoint:** `POST /api/v1/auth/login`
- **Quyền:** Public (có bảo vệ chống brute-force qua Rate Limiter)
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "Nguyễn Văn A",
      "phone_number": "0912345678",
      "role": "USER",
      "is_active": true,
      "avatar_url": null,
      "created_at": "2026-10-14T13:30:00Z"
    }
  },
  "message": "Đăng nhập thành công"
}
```

---

### 2.3. Đăng xuất
- **Endpoint:** `POST /api/v1/auth/logout`
- **Quyền:** Bearer Token
- **Headers:** `Authorization: Bearer <token>`
- **Response (200 OK):**
```json
{
  "success": true,
  "data": { "user_id": 1 },
  "message": "Đăng xuất thành công"
}
```

---

### 2.4. Xem Hồ Sơ Cá Nhân
- **Endpoint:** `GET /api/v1/users/me`
- **Quyền:** Bearer Token (Authenticated User)
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "phone_number": "0912345678",
    "role": "USER",
    "is_active": true,
    "avatar_url": null,
    "created_at": "2026-10-14T13:30:00Z"
  },
  "message": "Lấy thông tin tài khoản thành công"
}
```

---

### 2.5. Cập Nhật Hồ Sơ Cá Nhân
- **Endpoint:** `PUT /api/v1/users/me`
- **Quyền:** Bearer Token (Authenticated User)
- **Request Body:**
```json
{
  "full_name": "Nguyễn Văn A (Mới)",
  "phone_number": "0988776655",
  "avatar_url": "https://res.cloudinary.com/demo/avatar.jpg"
}
```
- **Response (200 OK):** Trả về `UserResponse` đã cập nhật.

---

## 3. Phân Hệ Quản Trị Người Dùng (Admin Only)

### 3.1. Danh Sách & Tìm Kiếm Người Dùng
- **Endpoint:** `GET /api/v1/users`
- **Quyền:** ADMIN Only (Token phải có `role == "ADMIN"`)
- **Query Params:**
  - `page` (int, default: 1)
  - `size` (int, default: 10, max: 100)
  - `role` (str, optional: "USER" hoặc "ADMIN")
  - `is_active` (bool, optional)
  - `search` (str, optional: tìm kiếm theo tên, email, số điện thoại)
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "email": "user@example.com",
        "full_name": "Nguyễn Văn A",
        "phone_number": "0912345678",
        "role": "USER",
        "is_active": true,
        "avatar_url": null,
        "created_at": "2026-10-14T13:30:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "total_pages": 1
  },
  "message": "Lấy danh sách người dùng thành công"
}
```

---

### 3.2. Khóa / Mở Khóa Tài Khoản
- **Endpoint:** `PATCH /api/v1/users/{id}/status`
- **Quyền:** ADMIN Only
- **Request Body:**
```json
{
  "is_active": false
}
```
- **Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "phone_number": "0912345678",
    "role": "USER",
    "is_active": false,
    "avatar_url": null,
    "created_at": "2026-10-14T13:30:00Z"
  },
  "message": "Đã khóa tài khoản thành công"
}
```
*(Tài khoản sau khi bị khóa nếu thực hiện yêu cầu mới sẽ bị chặn với mã `403 USER_INACTIVE`).*

---

## 4. Hướng Dẫn Chạy Migration Database (Alembic)

Toàn bộ 10 bảng dữ liệu theo ERD đã được đóng gói trong revision `001_initial_schema`.

1. Khởi động PostgreSQL:
```powershell
docker compose up -d
```
2. Thực thi migration lên database PostgreSQL:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```
3. Kiểm tra phiên bản hiện tại trên database:
```powershell
alembic current
```
*(Kết quả mong đợi: `001_initial_schema (head)`).*
