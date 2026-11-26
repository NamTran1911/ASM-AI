# Hệ thống Quản lý & Phân loại Đơn hàng Tự động

Đồ án môn **Phát triển ứng dụng AI với Python** xây dựng bằng **FastAPI**, **CSV Storage**, **scikit-learn** và **OpenAI API**.

## Chức năng chính
- **Quản lý đơn hàng (CRUD)**: Thêm, xem, tìm kiếm, lọc, sửa, xóa đơn hàng trên giao diện web.
- **Phân loại độ ưu tiên (ML)**: Tiền xử lý mô tả sản phẩm và vector hóa bằng `TfidfVectorizer`, phân loại `High / Medium / Low` bằng `LogisticRegression` (nạp từ `models/model.pkl`).
- **Tự động soạn email (LLM + BackgroundTasks)**: Đơn hàng `High` tự động kích hoạt `BackgroundTasks` gọi OpenAI (hoặc Gemini / mẫu dự phòng) soạn email và lưu vào bảng `order_logs`.
- **Bảo mật API**: Hỗ trợ xác thực qua header `X-API-Key` khi bật `REQUIRE_API_KEY=true`.

## Cấu trúc thư mục
- `app/main.py`: Khởi tạo FastAPI và toàn bộ API endpoints.
- `app/database.py`: Đọc/ghi dữ liệu đơn hàng từ `orders_test_1000.csv` và log email từ `order_logs.csv`.
- `app/schemas.py`: Schema kiểm tra dữ liệu đầu vào/ra bằng Pydantic.
- `app/ml.py`: Load `model.pkl` & `vectorizer.pkl` để dự đoán độ ưu tiên.
- `app/services.py`: Hàm gọi OpenAI/Gemini soạn email và lưu log ở background.
- `ml_training/`: Script tạo dữ liệu mẫu (`generate_dataset.py`) và huấn luyện model (`train.py`).
- `api/index.py` & `vercel.json`: Cấu hình deploy lên Vercel.

## Cách chạy trên máy (Local)
1. Cài đặt thư viện:
```bash
pip install -r requirements.txt
```
2. Tạo file `.env` (copy từ `.env.example`):
```env
ORDERS_CSV_PATH=orders_test_1000.csv
ORDER_LOGS_CSV_PATH=order_logs.csv
OPENAI_API_KEY=
```
3. (Tuỳ chọn) Huấn luyện lại model ML:
```bash
python ml_training/generate_dataset.py
python ml_training/train.py
```
4. Chạy server:
```bash
uvicorn app.main:app --reload --port 8000
```
Mở trình duyệt tại `http://localhost:8000` (hoặc `http://localhost:8000/docs` để xem Swagger API).

5. Chạy test:
```bash
python test_app.py
```
