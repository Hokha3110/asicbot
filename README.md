# 🛡️ SECURITY SOLUTION COPILOT
> **Enterprise AI Assistant for Security Presales Architects & Solution Engineers**
> Trợ lý AI chuyên biệt hỗ trợ Presales tra cứu, thấu hiểu và tư vấn giải pháp An toàn thông tin từ tài liệu PDF / DOCX / PPTX.

---

## 🌟 1. Tổng Quan Hệ Thống

**Security Solution Copilot** là nền tảng web nội bộ chuẩn Clean Architecture kết hợp sức mạnh của:
- **Retrieval-Augmented Generation (RAG)** với ChromaDB Vector Store & PyMuPDF/DOCX/PPTX parser.
- **Chuẩn hóa phản hồi Presales 8 phần**: Solution, Category, Problem solved, Key capability, Use case, Customer discovery questions, Competitor/Alternative, Source reference.
- **5 Chế độ Presales độc quyền**: `[Technical Explanation]`, `[Customer Explanation]`, `[Sales Pitch]`, `[Email Draft]`, `[Create Slide]`.
- **Smart NLP Intent Search**: Tự động nhận diện nhu cầu/nỗi đau của khách hàng để map tới giải pháp chính xác (VD: "kiểm tra hacker có vượt qua hệ thống không" -> Picus BAS; "biết dữ liệu nhạy cảm nằm ở đâu" -> DSPM).
- **Solution Battle Cards Hub**: Quản trị vũ khí cạnh tranh, xử lý phản bác (Objection Handling) và tạo Battle Card mới tức thì bằng AI.

---

## 🏗️ 2. Tech Stack & Kiến Trúc Triển Khai

| Layer | Công nghệ | Nền tảng triển khai |
| :--- | :--- | :--- |
| **Frontend (FE)** | React 18, TypeScript, Vite, TailwindCSS, Lucide Icons | **Vercel** |
| **Backend (BE)** | Python FastAPI (Async, REST API), SQLAlchemy ORM | **Ubuntu Linux 22.04 LTS** / Docker |
| **Database** | PostgreSQL 16 / SQLite Local | Ubuntu Linux 22.04 |
| **Vector DB** | ChromaDB (Persistent Vector Store) + Sentence-Transformers | Ubuntu Linux 22.04 |
| **AI LLM Engine** | OpenAI GPT-4o-mini & Ollama Local LLM (`llama3:8b`, `qwen2.5`) | Cloud API / Local Server |
| **Document Parsers** | PyMuPDF (`fitz`), `python-docx`, `python-pptx` | Backend Engine |

---

## 🚀 3. Hướng Dẫn Deploy Chi Tiết

### A. Deploy Backend lên Linux Ubuntu 22.04 LTS

#### Cách 1: Sử dụng Script cài đặt tự động (Khuyên dùng)
```bash
# 1. Clone repository về máy chủ Ubuntu
git clone https://github.com/your-org/security-copilot.git /opt/security-copilot
cd /opt/security-copilot/backend

# 2. Cấp quyền thực thi và chạy script cài đặt
chmod +x setup_ubuntu_2204.sh
./setup_ubuntu_2204.sh
```

#### Cách 2: Sử dụng Docker Compose trên Ubuntu 22.04
```bash
cd /opt/security-copilot

# 1. Cấu hình file môi trường
cp .env.example .env
nano .env # Điền OPENAI_API_KEY nếu có

# 2. Khởi chạy toàn bộ PostgreSQL và FastAPI Backend
docker compose up -d --build

# 3. Kiểm tra trạng thái
docker compose ps
curl http://localhost:8000/api/health
```

#### Cấu hình Nginx Reverse Proxy trên Ubuntu 22.04:
```nginx
# /etc/nginx/sites-available/security-copilot
server {
    listen 80;
    server_name api.yourdomain.com; # hoặc địa chỉ IP của server

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### B. Deploy Frontend lên Vercel

1. Đăng nhập vào [Vercel Dashboard](https://vercel.com).
2. Bấm **Add New...** -> **Project** -> Chọn repository này.
3. Trong phần **Root Directory**, chọn thư mục `frontend`.
4. Cấu hình **Environment Variables**:
   - `VITE_API_BASE_URL`: URL Backend chạy trên Ubuntu (Ví dụ: `https://api.yourdomain.com/api/v1` hoặc `http://YOUR_UBUNTU_IP:8000/api/v1`).
5. Bấm **Deploy**. Vercel sẽ tự động build với `vercel.json` đã được định cấu hình sẵn SPA Rewrite rules.

---

## 💻 4. Chạy Local trên Máy Phát Triển

### 1. Khởi động Backend:
```bash
cd backend
python -m venv venv
# Trên Windows:
.\venv\Scripts\activate
# Trên Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/api/health`

#### Cấu hình Google Login

Trong Google Cloud Console, tạo OAuth Client loại **Web application** và thêm đúng redirect URI:

```text
http://localhost:8000/api/v1/auth/google/callback
https://api.yourdomain.com/api/v1/auth/google/callback
```

Điền các biến `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`, `GOOGLE_ADMIN_EMAILS` và `FRONTEND_URL` trong file `.env`. Email nằm trong `GOOGLE_ADMIN_EMAILS` (phân tách bằng dấu phẩy) sẽ được cấp role `admin`; tài khoản Google khác mặc định là `user`.

### 2. Khởi động Frontend:
```bash
cd frontend
npm install
npm run dev
```
- Truy cập giao diện: `http://localhost:5173`

## ☁️ 5. Đưa source lên GitHub và deploy Cloudflare

### Cấu trúc deploy

- `frontend/`: deploy lên **Cloudflare Pages**.
- `backend/`: chạy trên Linux/Docker/VM, sau đó frontend gọi qua API URL public.
- `backend/chroma_db/`, `backend/uploaded_docs/` và database local là dữ liệu runtime, không đưa lên GitHub.

### GitHub

```bash
cp .env.example .env
git add .
git commit -m "Prepare Kali0t for deployment"
git push origin main
```

Không commit `.env`, OAuth secret, service account JSON, `node_modules`, `dist`, database hoặc ChromaDB.

### Cloudflare Pages

Trong Cloudflare Pages, chọn repository GitHub và đặt **Root directory** là `frontend`:

```text
Build command: npm run build
Build output directory: dist
```

Thêm environment variable cho môi trường Production:

```text
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```

Frontend có sẵn mẫu local tại `frontend/.env.example`; trên Cloudflare Pages hãy khai báo biến này trong **Settings > Environment variables**, không commit file `.env` thật.

File `frontend/public/_redirects` đã được thêm để SPA routing không trả về 404 khi refresh trang. Có thể deploy bằng CLI:

```bash
cd frontend
npm install
npx wrangler login
npm run deploy:cloudflare -- --project-name kali0t
```

### Backend Linux

Backend không chạy trực tiếp trên Cloudflare Pages. Giữ backend trên Linux/Docker:

```bash
cp .env.example .env
# Điền SECRET_KEY, GOOGLE_CLIENT_ID/SECRET, GOOGLE_REDIRECT_URI,
# FRONTEND_URL và CORS_ORIGINS theo domain thật
docker compose up -d --build
```

Redirect URI Google OAuth khi production phải là:

```text
https://api.yourdomain.com/api/v1/auth/google/callback
```

---

## 🔑 5. Tài Khoản & Dữ Liệu Mẫu Có Sẵn

Hệ thống đã tự động kích hoạt và nạp sẵn tài khoản và tài liệu:

| Tài khoản | Mật khẩu | Quyền hạn (Role) | Chức năng chính |
| :--- | :--- | :--- | :--- |
| `admin` | `Admin@123456` | **Admin** | Toàn quyền Upload, Phân tích tài liệu, Thêm sửa giải pháp |
| `presales_user` | `Presales@123` | **User** | Tra cứu AI Chat, Smart Search, Xem Battle Cards, Security Academy |

### Danh mục Giải pháp Nạp Sẵn:
1. **Picus Complete Security Validation** (Vendor: Picus Security - BAS & CTEM)
2. **Netwrix DSPM** (Vendor: Netwrix - Data Security Posture Management)
3. **Netwrix Access Analyzer** (Vendor: Netwrix - Identity Governance & Least Privilege)
4. **Certus Solution** (Vendor: Certus - DevSecOps & Cloud Posture)
5. **Graylog Security** (Vendor: Graylog - SIEM & SOC Log Management)
6. **Trend Micro Vision One XDR** (Vendor: Trend Micro - Extended Detection & Response)
7. **Forcepoint DSPM & DLP** (Vendor: Forcepoint - Data Protection)

---

## 📊 6. Cấu Trúc Thư Mục Clean Architecture

```text
asicbot/
├── .env.example                    # Cấu hình biến môi trường
├── docker-compose.yml              # Triển khai Docker trên Ubuntu 22.04
├── README.md                       # Tài liệu hướng dẫn
│
├── backend/                        # FastAPI Backend
│   ├── Dockerfile
│   ├── setup_ubuntu_2204.sh       # Script cài đặt tự động trên Linux 22.04
│   ├── systemd/
│   │   └── security-copilot-be.service # Systemd Service
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # Entry point
│       ├── config.py               # Settings
│       ├── database.py             # SQLAlchemy Engine
│       ├── models/                 # SQLAlchemy Entities
│       ├── schemas/                # Pydantic Schemas
│       ├── services/               # RAG, Parsers, LLM, Battlecard, Quiz
│       ├── routers/                # REST Endpoints
│       └── seed/                   # Data Seeder & PDF auto-ingestion
│
└── frontend/                       # React + Vite + Tailwind Frontend
    ├── package.json
    ├── vercel.json                 # Cấu hình Deploy Vercel
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── App.tsx
        ├── types/
        ├── services/api.ts
        └── components/
            ├── layout/             # Sidebar, Header, RightPanel
            ├── chat/               # ChatWindow, PresalesActions, SourceBadge
            ├── documents/          # DocumentCenter, FileUploadModal
            ├── solutions/          # SolutionCatalog, SmartSearch, DetailModal
            ├── battlecards/        # BattleCardHub, BattleCardDetail
            ├── academy/            # SecurityAcademy, QuizCard
            └── settings/           # SettingsModal
```
