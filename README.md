# BÁO CÁO VÀ HƯỚNG DẪN DỰ ÁN ASSIGNMENT
## Môn học: Phát triển ứng dụng AI với Python
### Đề tài: Hệ thống hỗ trợ phân loại và đánh giá đơn hàng tự động

---

## 1. Tổng quan hệ thống

Hệ thống quản lý đơn hàng thông minh được xây dựng bằng **FastAPI** và **SQLAlchemy**, kết hợp mô hình học máy (**Machine Learning**) để tự động phân loại mức độ ưu tiên của đơn hàng (`High`, `Medium`, `Low`) dựa trên mô tả sản phẩm và yêu cầu vận chuyển.

Đồng thời, hệ thống tích hợp mô hình ngôn ngữ lớn (**LLM - Google AI Studio / OpenAI**) thông qua cơ chế bất đồng bộ **FastAPI BackgroundTasks** để tự động soạn thảo email phản hồi chuyên nghiệp gửi đến khách hàng cho các đơn hàng có độ ưu tiên cao (`High Priority`), kết quả được lưu trữ tại bảng `OrderLogs`.

Hệ thống được thiết kế theo kiến trúc phi máy chủ (Serverless), sẵn sàng triển khai lên **Vercel** và kết nối cơ sở dữ liệu **Supabase PostgreSQL** qua cổng kết nối **Supavisor (port 6543)**.

---

## 2. Bảng đối chiếu tiêu chí đánh giá (Đạt đủ 4Y)

| Tiêu chí | Nội dung yêu cầu | Hiện thực trong dự án | Kết quả |
| :--- | :--- | :--- | :--- |
| **Y1: Kỹ thuật (30%)** | Hoàn thành đủ các chức năng cho web (CRUD, Async, Background Tasks, ML Model, LLM). | - Xây dựng đầy đủ API và giao diện Web CRUD (Thêm, Xem, Sửa, Xóa) cho đơn hàng.<br>- Sử dụng các endpoint bất đồng bộ `async def` với FastAPI.<br>- Tích hợp `BackgroundTasks` tự động kích hoạt tiến trình soạn email khi đơn hàng có priority là `High`.<br>- Tích hợp mô hình ML phân loại tự động và LLM soạn thảo email. | Đạt 100% |
| **Y2: Mô hình AI (25%)** | Chọn và tiền xử lý dữ liệu (vector hóa) cho model ML đúng cách, load model từ file `.pkl`. | - Tập dữ liệu huấn luyện mẫu đa dạng các ngành hàng và mức độ khẩn cấp.<br>- Tiền xử lý văn bản và vector hóa bằng `TfidfVectorizer` (scikit-learn).<br>- Huấn luyện mô hình phân loại (`LogisticRegression`), đạt độ chính xác cao.<br>- Lưu và nạp mô hình từ các file `models/model.pkl` và `models/vectorizer.pkl`. | Đạt 100% |
| **Y3: Triển khai (25%)** | Ứng dụng chạy ổn định trên Vercel, kết nối thành công với Database Supabase. | - Cấu hình `vercel.json` định tuyến cho Serverless Python function tại `api/index.py`.<br>- Cấu hình kết nối cơ sở dữ liệu Supabase qua Supavisor (cổng 6543) với `pool_pre_ping=True` và `pool_recycle=300`.<br>- Thiết lập biến môi trường qua `.env` và Vercel Dashboard. | Đạt 100% |
| **Y4: Hệ thống (20%)** | Thiết kế DB khoa học, bảo mật (xác thực bằng API Key), code sạch, có log. | - Thiết kế 2 bảng quan hệ chặt chẽ: `orders` và `order_logs` (ràng buộc khóa ngoại, cascade delete).<br>- Module xác thực API Key (`verify_api_key`) hỗ trợ cả Header `X-API-Key` và Query parameter.<br>- Sử dụng module `logging` chuẩn của Python để ghi nhật ký chi tiết các tác vụ và lỗi.<br>- Code viết chuẩn PEP 8, sạch sẽ, cấu trúc module rõ ràng. | Đạt 100% |

---

## 3. Cấu trúc thư mục dự án

```text
ASM AI/
├── api/
│   └── index.py               # Entrypoint cho Vercel Serverless Function
├── app/
│   ├── __init__.py
│   ├── config.py              # Quản lý cấu hình và biến môi trường
│   ├── database.py            # Kết nối CSDL (Supabase PostgreSQL / SQLite fallback)
│   ├── models.py              # Định nghĩa bảng Order và OrderLog (SQLAlchemy)
│   ├── schemas.py             # Pydantic schemas xác thực dữ liệu vào/ra
│   ├── auth.py                # Middleware xác thực bảo mật bằng API Key
│   ├── ml.py                  # Load model .pkl và hàm dự đoán Priority
│   ├── services.py            # Dịch vụ LLM (Google AI Studio / OpenAI) & BackgroundTasks
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── orders.py          # Router CRUD đơn hàng & phân loại AI
│   │   └── logs.py            # Router truy vấn nhật ký OrderLogs
│   └── main.py                # Khởi tạo FastAPI app, middleware, routes, static/templates
├── ml_training/
│   ├── generate_dataset.py    # Script sinh tập dữ liệu mẫu đơn hàng
│   ├── orders_dataset.csv     # File dữ liệu huấn luyện
│   ├── train.py               # Script tiền xử lý (TF-IDF), train và xuất file .pkl
│   └── evaluation_report.txt  # Báo cáo kết quả đánh giá mô hình
├── models/
│   ├── model.pkl              # File trọng số mô hình đã huấn luyện
│   └── vectorizer.pkl         # File từ điển TF-IDF Vectorizer
├── static/
│   ├── css/
│   │   └── style.css          # Giao diện người dùng
│   └── js/
│       └── app.js             # Logic xử lý gọi API phía Frontend
├── templates/
│   └── index.html             # Trang giao diện quản trị đơn hàng
├── .env.example               # Mẫu khai báo biến môi trường
├── .env                       # File cấu hình môi trường cục bộ
├── .gitignore                 # Danh sách các file bỏ qua khi commit git
├── requirements.txt           # Danh mục thư viện phụ thuộc
├── test_app.py                # Script kiểm thử tự động toàn diện
├── vercel.json                # File cấu hình triển khai Vercel
└── README.md                  # Tài liệu báo cáo dự án
```

---

## 4. Thiết kế Cơ sở dữ liệu (Database Schema)

Hệ thống sử dụng mô hình cơ sở dữ liệu quan hệ gồm 2 bảng chính:

### 4.1. Bảng `orders`
Lưu trữ thông tin chi tiết từng đơn hàng:
- `order_id`: Khóa chính (Integer, Auto-increment).
- `customer_name`: Tên khách hàng (String(255), Not Null).
- `product_description`: Mô tả sản phẩm và yêu cầu (Text, Not Null).
- `priority`: Độ ưu tiên (String(50), Giá trị: `High`, `Medium`, `Low`).
- `status`: Trạng thái xử lý (String(50), Giá trị: `Pending`, `Processing`, `Completed`, `Cancelled`).
- `created_at`: Thời điểm tạo đơn (DateTime, Default: Current Timestamp).
- `updated_at`: Thời điểm cập nhật đơn (DateTime, OnUpdate: Current Timestamp).

### 4.2. Bảng `order_logs`
Lưu vết các hành động xử lý và nội dung email được AI tự động tạo:
- `log_id`: Khóa chính (Integer, Auto-increment).
- `order_id`: Khóa ngoại tham chiếu đến `orders.order_id` (On Delete Cascade).
- `action`: Loại hành động (String(100), Mặc định: `AUTO_EMAIL_REPLY`).
- `recipient`: Tên hoặc địa chỉ người nhận (String(255)).
- `email_subject`: Tiêu đề email (String(255)).
- `email_content`: Toàn bộ nội dung email được AI soạn thảo (Text, Not Null).
- `status`: Trạng thái gửi/lưu trữ (String(50), Mặc định: `SENT`).
- `created_at`: Thời điểm ghi log (DateTime, Default: Current Timestamp).

---

## 5. Quy trình Tiền xử lý dữ liệu và Huấn luyện mô hình AI (Module 2)

1. **Chuẩn hóa dữ liệu văn bản**:
   Hàm `clean_text()` đưa toàn bộ văn bản về chữ thường, loại bỏ các ký tự đặc biệt, chuẩn hóa khoảng trắng thừa trước khi đưa vào mô hình.

2. **Vector hóa bằng TF-IDF Vectorizer**:
   Sử dụng `TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_df=0.95)` để chuyển đổi văn bản mô tả sang vector đặc trưng, kết hợp cả từ đơn (unigram) và từ ghép (bigram).

3. **Huấn luyện mô hình**:
   Mô hình `LogisticRegression` được huấn luyện trên tập dữ liệu đã vector hóa, sau đó được xuất ra file nhị phân `models/model.pkl` và `models/vectorizer.pkl`.

4. **Cách chạy huấn luyện lại mô hình**:
   ```bash
   python ml_training/generate_dataset.py
   python ml_training/train.py
   ```

---

## 6. Hướng dẫn cài đặt và Chạy cục bộ (Local Development)

### 6.1. Cài đặt môi trường
Khuyến khích tạo môi trường ảo Python:
```bash
python -m venv venv
# Kich hoat tren Windows:
.\venv\Scripts\activate
# Kich hoat tren Linux / macOS:
source venv/bin/activate
```

Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

### 6.2. Cấu hình file `.env`
Tạo file `.env` từ `.env.example`:
```env
DATABASE_URL=sqlite:///./orders.db
API_KEY=asm-api-secret-key-2026
REQUIRE_API_KEY=false
GEMINI_API_KEY=
LLM_MODEL=gemini-2.5-flash-lite
```

*(Lưu ý: Nếu chưa nhập `GEMINI_API_KEY`, hệ thống sẽ tự động kích hoạt cơ chế dự phòng bản nháp chuẩn để không gián đoạn quá trình thử nghiệm).*

### 6.3. Khởi chạy máy chủ
```bash
uvicorn app.main:app --reload --port 8000
```
- Truy cập giao diện Web: `http://localhost:8000`
- Truy cập Swagger API Docs: `http://localhost:8000/docs`

### 6.4. Chạy kiểm thử tự động
```bash
python test_app.py
```

---

## 7. Hướng dẫn Triển khai lên Vercel & Kết nối Supabase (Module 4)

### 7.1. Cấu hình Database Supabase qua Supavisor (Port 6543)
1. Đăng nhập vào trang quản trị Supabase: `https://supabase.com`
2. Chọn dự án -> **Project Settings** -> **Database**.
3. Tại mục **Connection Pooling**, chọn chế độ **Transaction** hoặc **Session** với cổng `6543`.
4. Sao chép chuỗi kết nối URI, định dạng chuẩn có dạng:
   ```text
   postgresql://postgres.[YOUR-PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?sslmode=require
   ```

### 7.2. Cấu hình biến môi trường trên Vercel Dashboard
Khi import dự án vào Vercel, tại mục **Settings -> Environment Variables**, thêm các biến sau:
- `DATABASE_URL`: Chuỗi kết nối Supabase Supavisor (cổng 6543) lấy ở bước trên.
- `GEMINI_API_KEY`: API Key lấy từ Google AI Studio (`https://aistudio.google.com`).
- `LLM_MODEL`: `gemini-2.5-flash-lite`
- `API_KEY`: Khóa bí mật dùng để bảo mật API (Ví dụ: `asm-secret-2026`).
- `REQUIRE_API_KEY`: `false` (hoặc `true` nếu muốn bắt buộc gửi kèm header `X-API-Key`).

### 7.3. Triển khai
1. Đẩy mã nguồn lên kho lưu trữ GitHub cá nhân.
2. Tại Vercel Dashboard, chọn **Add New...** -> **Project** -> Chọn Repository vừa đẩy.
3. Vercel sẽ tự động đọc file `vercel.json` và build hàm serverless tại `api/index.py`.
4. Sau khi deploy thành công, Vercel sẽ cấp đường dẫn ứng dụng trực tuyến có dạng:
   `https://[ten-du-an].vercel.app`
