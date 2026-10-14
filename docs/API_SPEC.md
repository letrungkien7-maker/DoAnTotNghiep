# ĐẶC TẢ REST API (API SPECIFICATION)

Base URL: `http://127.0.0.1:8000/api/v1`

## 1. System & Health Check
| Method | Endpoint | Quyền | Mô tả |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Public | Kiểm tra trạng thái ứng dụng & ping cơ sở dữ liệu |
| `GET` | `/` | Public | Thông tin phiên bản & link Swagger docs |

### Response mẫu `/api/v1/health`
```json
{
  "status": "healthy",
  "app_name": "Real Estate Business API",
  "environment": "development",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "dialect": "postgresql",
    "latency_ms": 14.2,
    "error": null
  },
  "timestamp": "2026-10-14T13:00:00.000Z"
}
```

## 2. Kế hoạch Endpoints các phân hệ tiếp theo
- `POST /api/v1/auth/register` & `POST /api/v1/auth/login`: Xác thực JWT
- `GET, POST, PUT, DELETE /api/v1/listings`: Quản lý tin đăng BĐS
- `GET /api/v1/admin/listings/pending`: Kiểm duyệt tin đăng
- `GET /api/v1/recommendations/similar/{id}`: Gợi ý BĐS tương đồng
- `POST /api/v1/chat/messages`: Tương tác Chatbot LLM
