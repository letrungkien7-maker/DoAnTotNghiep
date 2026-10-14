# Hệ Thống Kinh Doanh Bất Động Sản Tích Hợp Chatbot & Gợi Ý Thông Minh

Dự án đồ án tốt nghiệp: **THIẾT KẾ VÀ PHÁT TRIỂN HỆ THỐNG KINH DOANH BẤT ĐỘNG SẢN TÍCH HỢP CHATBOT VÀ HỆ THỐNG GỢI Ý THÔNG MINH**.

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons.
- **Backend:** Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic.
- **Database:** PostgreSQL 16 Alpine.
- **AI & NLP:** Content-Based Recommendation Engine, Hybrid Scoring, Deterministic Vietnamese NLP Extractor, Multi-turn Chatbot Memory & Anti-Hallucination Grounding.
- **Testing:** Pytest (67/67 passed), Vitest (10/10 passed).
- **Deployment:** Docker & Docker Compose Multi-Stage, Nginx Reverse Proxy, Automated Backup/Restore.

---

## 1. Khởi Chạy Nhanh 1-Lệnh Với Docker Compose (Production-Ready)

Để chạy toàn bộ hệ thống gồm Database PostgreSQL, Backend FastAPI và Frontend React/Nginx:

```bash
# 1. Sao chép cấu hình môi trường
cp .env.production.example .env

# 2. Khởi chạy toàn bộ hệ thống
docker compose up -d --build
```

- **Frontend Web UI:** `http://localhost` (hoặc `http://localhost:80`)
- **Backend API:** `http://localhost:8000`
- **Swagger API Docs:** `http://localhost:8000/docs`
- **PostgreSQL Database:** `localhost:5432`

---

## 2. Hướng Dẫn Cài Đặt Cục Bộ (Local Development)

### 2.1. Yêu Cầu Tiên Quyết (Prerequisites)
- Python 3.10+
- Node.js 18+ (khuyên dùng Node 20 LTS)
- PostgreSQL 16 (cài đặt trực tiếp hoặc chạy container `docker compose up -d postgres`)
- Git

### 2.2. Khởi Động Database & Chạy Migrations
```bash
# Khởi chạy PostgreSQL qua docker compose
docker compose up -d postgres

# Chuyển vào thư mục backend và tạo môi trường ảo
cd backend
python -m venv .venv

# Kích hoạt môi trường ảo:
# Trên Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Trên Linux/macOS:
source .venv/bin/activate

# Cài đặt thư viện Python
pip install -r requirements.txt

# Cấu hình file .env
copy .env.example .env   # (hoặc cp .env.example .env trên Linux)

# Chạy migration đồng bộ schema cơ sở dữ liệu
alembic upgrade head
```

### 2.3. Khởi Tạo Dữ Liệu Mẫu Cho Buổi Demo (Seed Data)
Chạy script seed dữ liệu để tự động tạo tài khoản Admin, Seller, Buyer, 10 bất động sản mẫu và tương tác:

```bash
# Chạy từ thư mục gốc
python seed.py

# Hoặc chạy từ thư mục backend
python -m app.scripts.seed_demo_data
```

**Tài khoản đăng nhập sẵn sàng để bảo vệ đồ án:**
| Vai trò | Email đăng nhập | Mật khẩu | Mục đích sử dụng |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin@bds-smart.vn` | `Admin@123456` | Duyệt tin chờ duyệt, từ chối tin có lý do, quản lý tài khoản |
| **Môi giới (Seller)** | `seller@bds-smart.vn` | `Seller@123456` | Đăng tin mới, sửa tin, ẩn tin, theo dõi trạng thái kiểm duyệt |
| **Khách hàng (Buyer)** | `buyer@bds-smart.vn` | `Buyer@123456` | Tìm kiếm, trải nghiệm gợi ý cá nhân hóa, chat AI, lưu yêu thích |

### 2.4. Khởi Chạy Backend API
```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Healthcheck: `http://127.0.0.1:8000/api/v1/health`
- Swagger UI: `http://127.0.0.1:8000/docs`

### 2.5. Khởi Chạy Frontend UI
```bash
cd frontend
npm install
npm run dev
```
- Giao diện người dùng: `http://localhost:5173`

---

## 3. Kiểm Thử Tự Động (Automated Testing)

### 3.1. Backend Pytest (67 Tests)
```bash
cd backend
.venv\Scripts\python.exe -m pytest -v
```
Bao gồm:
- `tests/test_auth.py`: Đăng ký, đăng nhập JWT, hash mật khẩu bcrypt.
- `tests/test_rbac.py`: Phân quyền Admin, User, ngăn truy cập tài nguyên của người khác.
- `tests/test_listings.py`: CRUD tin đăng, vòng đời trạng thái (Draft, Pending, Approved, Rejected, Hidden, Expired).
- `tests/test_interactions.py`: Lưu yêu thích, gửi form tư vấn, lịch sử xem.
- `tests/test_recommendations.py`: Thuật toán scoring đa tiêu chí, personalized feed, item similarity.
- `tests/test_chatbot.py`: Trích xuất NLP tiếng Việt, hội thoại đa lượt tích lũy ngữ cảnh, chống ảo giác, API chat sessions.

### 3.2. Frontend Vitest (10 Tests)
```bash
cd frontend
npm test
```
Bao gồm kiểm thử component, định dạng tiền tệ VNĐ/m², layout và service gọi API Chatbot.

### 3.3. Kiểm Tra Build Production
```bash
cd frontend
npm run build
```

---

## 4. Sao Lưu & Khôi Phục Cơ Sở Dữ Liệu (Backup & Restore)

### Trên Windows PowerShell:
```powershell
# Sao lưu cơ sở dữ liệu
.\scripts\backup_db.ps1

# Khôi phục từ file sao lưu
.\scripts\restore_db.ps1 -BackupFile .\backups\bds_backup_YYYYMMDD_HHMMSS.sql
```

### Trên Linux / VPS:
```bash
# Cấp quyền thực thi
chmod +x scripts/*.sh

# Sao lưu cơ sở dữ liệu (tự nén gzip)
./scripts/backup_db.sh

# Khôi phục từ file sao lưu
./scripts/restore_db.sh backups/bds_backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 5. Tài Liệu Nghiệp Vụ & Báo Cáo Đồ Án

- [Kiến trúc hệ thống chi tiết](docs/ARCHITECTURE.md)
- [Đặc tả toàn bộ REST API](docs/API_SPEC.md)
- Báo cáo thuyết minh tốt nghiệp toàn diện & Kịch bản bảo vệ: Xem thư mục tài liệu Artifacts.
