# Hệ Thống Kinh Doanh Bất Động Sản Tích Hợp Chatbot & Gợi Ý Thông Minh

Dự án đồ án tốt nghiệp: Nền tảng thương mại bất động sản ứng dụng AI (Chatbot LLM & Content-Based Recommendation Engine).

---

## 1. Cấu Trúc Thư Mục Dự Án

```text
Web_Kien/
├── .gitignore               # Cấu hình bỏ qua file nhạy cảm, cache, venv, node_modules
├── docker-compose.yml       # Khởi chạy PostgreSQL 16 (Port 5432)
├── README.md                # Tài liệu hướng dẫn cài đặt & vận hành
├── docs/                    # Tài liệu kiến trúc & đặc tả API
│   ├── ARCHITECTURE.md
│   └── API_SPEC.md
├── backend/                 # Ứng dụng Backend FastAPI + SQLAlchemy
│   ├── .env.example         # Mẫu biến môi trường
│   ├── .env                 # Biến môi trường cục bộ (không commit Git)
│   ├── requirements.txt     # Danh sách thư viện Python
│   ├── pyproject.toml       # Cấu hình Ruff, Mypy, Pytest
│   ├── alembic.ini          # Cấu hình công cụ migration Alembic
│   ├── alembic/             # Thư mục quản lý migration phiên bản DB
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── app/                 # Mã nguồn chính của FastAPI
│   │   ├── main.py          # Entrypoint ứng dụng & cấu hình CORS
│   │   ├── api/v1/          # Routers API phiên bản 1 (/health, ...)
│   │   ├── core/            # Config, Security, Database session & connection ping
│   │   ├── models/          # SQLAlchemy Declarative Models (Base)
│   │   └── schemas/         # Pydantic Schemas (HealthResponse, ...)
│   └── tests/               # Bộ kiểm thử Pytest
│       ├── conftest.py
│       ├── test_health.py
│       └── test_db_connection.py
└── frontend/                # Ứng dụng Frontend React + Vite + TypeScript
    ├── .env.example         # Mẫu biến môi trường frontend
    ├── .env                 # Cấu hình API endpoint cục bộ
    ├── package.json         # Danh sách packages & lệnh chạy
    ├── vite.config.ts       # Cấu hình Vite, Alias @/, và Vitest
    ├── tsconfig.json        # Cấu hình TypeScript
    ├── tailwind.config.js   # Cấu hình Tailwind CSS
    ├── index.html           # File HTML gốc
    ├── src/
    │   ├── main.tsx         # Điểm khởi chạy React
    │   ├── App.tsx          # Router & Layout chính
    │   ├── components/      # Component giao diện (HealthStatus, ...)
    │   ├── services/        # Axios Client & API helper
    │   ├── types/           # Định nghĩa kiểu dữ liệu TypeScript
    │   └── test/            # Kiểm thử Vitest + React Testing Library
    │       ├── setup.ts
    │       └── App.test.tsx
```

---

## 2. Yêu Cầu Môi Trường (Prerequisites)

- **Hệ điều hành:** Windows 10/11 (PowerShell hoặc Command Prompt).
- **Python:** 3.10 trở lên.
- **Node.js:** 18 trở lên (khuyên dùng Node 20 LTS).
- **Cơ sở dữ liệu:** PostgreSQL 16 (Chạy trực tiếp hoặc qua Docker Desktop).
- **Git:** Đã cài đặt trên máy.

---

## 3. Hướng Dẫn Cài Đặt & Chạy Trên Windows (PowerShell)

### Bước 1: Khởi động Cơ sở dữ liệu PostgreSQL

**Cách 1: Sử dụng Docker Compose (Khuyên dùng)**
Mở PowerShell tại thư mục gốc `Web_Kien`:
```powershell
docker compose up -d
```
Container `real_estate_postgres` sẽ lắng nghe tại cổng `5432` với user `postgres`, password `postgres_password`, database `real_estate_db`.

**Cách 2: Sử dụng PostgreSQL cài trực tiếp trên Windows**
Tạo database tên `real_estate_db` trong pgAdmin hoặc `psql`:
```sql
CREATE DATABASE real_estate_db;
```
Cập nhật thông tin kết nối trong file `backend/.env`.

---

### Bước 2: Thiết lập & Chạy Backend (FastAPI)

1. Mở cửa sổ PowerShell mới, di chuyển vào thư mục `backend`:
```powershell
cd backend
```

2. Tạo và kích hoạt môi trường ảo Python:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(Nếu gặp lỗi script execution policy, xem mục 6 bên dưới).*

3. Cài đặt các thư viện phụ thuộc:
```powershell
pip install -r requirements.txt
```

4. Kiểm tra cấu hình môi trường:
Đảm bảo đã có file `.env` (sao chép từ `.env.example` nếu chưa có):
```powershell
Copy-Item .env.example .env
```

5. Khởi chạy máy chủ Backend:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **API Root:** `http://127.0.0.1:8000/`
- **Swagger UI (Interactive Docs):** `http://127.0.0.1:8000/docs`
- **Kiểm tra trạng thái (Health Check):** `http://127.0.0.1:8000/health` hoặc `http://127.0.0.1:8000/api/v1/health`

---

### Bước 3: Thiết lập & Chạy Frontend (React + Vite)

1. Mở một cửa sổ PowerShell khác, di chuyển vào thư mục `frontend`:
```powershell
cd frontend
```

2. Cài đặt các thư viện Node.js:
```powershell
npm install
```

3. Kiểm tra file `.env`:
```powershell
Copy-Item .env.example .env
```

4. Khởi chạy máy chủ phát triển Vite:
```powershell
npm run dev
```
Truy cập trình duyệt tại: `http://localhost:5173` để xem giao diện và bảng theo dõi trạng thái kết nối Backend + Database theo thời gian thực.

---

## 4. Kiểm Thử Hệ Thống (Automated Testing)

### 4.1. Chạy Kiểm Thử Backend (Pytest)
Tại thư mục `backend` (đã kích hoạt `.venv`):
```powershell
pytest
```
- Kiểm tra mã phản hồi HTTP của endpoint gốc `/`.
- Kiểm tra cấu trúc dữ liệu trả về của `/health` và `/api/v1/health`.
- Kiểm tra hàm chẩn đoán kết nối cơ sở dữ liệu `check_db_connection()` (hoạt động bền vững, không làm sập ứng dụng kể cả khi DB chưa bật).

### 4.2. Chạy Kiểm Thử Frontend (Vitest)
Tại thư mục `frontend`:
```powershell
# Chạy 1 lần (CI mode)
npm run test

# Chạy chế độ theo dõi (Watch mode)
npm run test:watch
```

### 4.3. Kiểm tra Định dạng & Linting
```powershell
# Backend (tại thư mục backend)
ruff check .

# Frontend (tại thư mục frontend)
npm run lint
npm run build
```

---

## 5. Cấu Hình Database Migration (Alembic)

Tại thư mục `backend` (đã kích hoạt `.venv`):

- **Tạo migration mới sau khi định nghĩa model:**
```powershell
alembic revision --autogenerate -m "Initial schema"
```
- **Áp dụng migration lên database:**
```powershell
alembic upgrade head
```
- **Xem trạng thái phiên bản hiện tại:**
```powershell
alembic current
```

---

## 6. Xử Lý Các Lỗi Thường Gặp Trên Windows

| Hiện tượng / Thông báo lỗi | Nguyên nhân | Cách khắc phục |
| :--- | :--- | :--- |
| `File ... cannot be loaded because running scripts is disabled on this system` | Windows PowerShell chặn chạy script theo chính sách ExecutionPolicy mặc định. | Chạy PowerShell với quyền Run as Administrator và thực thi: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| `psycopg2.OperationalError: connection to server at "localhost" port 5432 failed: Connection refused` | PostgreSQL service chưa được khởi động hoặc cổng 5432 bị chặn tường lửa. | Chạy `docker compose up -d` ở thư mục gốc hoặc khởi động service PostgreSQL trong Windows Services (`services.msc`). Endpoint `/health` được thiết kế tự bắt lỗi này và báo trạng thái `degraded` thay vì crash app. |
| `Port 8000 / 5173 is already in use` | Có tiến trình khác hoặc phiên chạy cũ đang chiếm cổng. | Tìm và tắt tiến trình: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess \| Stop-Process -Force` |
| `Property 'env' does not exist on type 'ImportMeta'` | Thiếu type definition cho Vite client trong TypeScript. | Đã cấu hình sẵn trong `frontend/src/vite-env.d.ts` với `/// <reference types="vite/client" />`. |
