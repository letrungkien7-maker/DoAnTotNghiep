# KIẾN TRÚC HỆ THỐNG (SYSTEM ARCHITECTURE)

## 1. Tổng quan Công nghệ
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, React Router v6.
- **Backend:** Python 3.10+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, psycopg2-binary.
- **Database:** PostgreSQL 16 (chạy qua Docker hoặc local instance).
- **Testing:** Pytest (Backend), Vitest + React Testing Library (Frontend).

## 2. Mô hình Kiến trúc Phân lớp
```
[React SPA Client]
        │ (REST API / JSON over HTTP)
        ▼
[FastAPI Router (/api/v1)]
        │
   ┌────┴───────────────────────────┐
   ▼                                ▼
[Service Layer]           [AI Subsystem (Future)]
(Listing, Auth, etc.)     (Chatbot LLM & RecEngine)
   │                                │
   ▼                                ▼
[Repository / ORM (SQLAlchemy 2.0)]
   │
   ▼
[PostgreSQL 16 Relational DB]
```

## 3. Quy chuẩn Mã nguồn
- **Backend:** Layered Architecture (`app/api`, `app/core`, `app/models`, `app/schemas`, `app/services`, `app/repositories`).
- **Frontend:** Feature-based modular structure (`src/components`, `src/features`, `src/services`, `src/types`).
- **Không lưu dữ liệu nhạy cảm:** Mọi thông tin bí mật (JWT Secret, DB credentials, API Keys) được nạp thông qua `.env`.
