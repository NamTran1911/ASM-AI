import os
import logging
from typing import List, Optional

from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import database
from app.schemas import OrderCreate, OrderUpdate, OrderOut, OrderLogOut, PredictRequest
from app.ml import predict_priority, model as ml_model
from app.services import send_email_background

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title="Hệ thống Quản lý Đơn hàng AI")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# Kiểm tra API Key nếu bật REQUIRE_API_KEY=true trong .env
def check_api_key(x_api_key: Optional[str] = Header(None)):
    require_key = os.getenv("REQUIRE_API_KEY", "false").lower() == "true"
    expected_key = os.getenv("API_KEY", "")
    if require_key and x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="API Key không hợp lệ")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "database": f"csv ({os.path.basename(database.get_orders_csv_path())})",
        "ml_model": "ready" if ml_model is not None else "fallback",
        "llm": "openai" if os.getenv("OPENAI_API_KEY") else ("gemini" if os.getenv("GEMINI_API_KEY") else "template"),
    }


@app.post("/api/orders/predict", dependencies=[Depends(check_api_key)])
async def predict_order_api(data: PredictRequest):
    return predict_priority(data.product_description)


@app.get("/api/orders", response_model=List[OrderOut], dependencies=[Depends(check_api_key)])
async def get_orders(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
):
    return database.list_orders(priority=priority, status=status, search=search)


@app.get("/api/orders/{order_id}", response_model=OrderOut, dependencies=[Depends(check_api_key)])
async def get_order_detail(order_id: int):
    order = database.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    return order


@app.post("/api/orders", response_model=OrderOut, status_code=201, dependencies=[Depends(check_api_key)])
async def create_order(order_in: OrderCreate, background_tasks: BackgroundTasks):
    # Nếu chưa chọn priority thì gọi ML dự đoán tự động
    priority = order_in.priority
    if priority not in ("High", "Medium", "Low"):
        priority = predict_priority(order_in.product_description)["priority"]

    new_order = database.create_order(
        customer_name=order_in.customer_name.strip(),
        product_description=order_in.product_description.strip(),
        priority=priority,
        status=order_in.status or "Pending",
    )

    # Đơn High Priority thì chạy background task soạn email
    if new_order["priority"] == "High":
        background_tasks.add_task(
            send_email_background,
            new_order["order_id"],
            new_order["customer_name"],
            new_order["product_description"],
        )

    return new_order


@app.put("/api/orders/{order_id}", response_model=OrderOut, dependencies=[Depends(check_api_key)])
async def update_order(order_id: int, order_in: OrderUpdate, background_tasks: BackgroundTasks):
    existing = database.get_order(order_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    old_priority = existing["priority"]
    order = database.update_order(
        order_id=order_id,
        customer_name=order_in.customer_name.strip() if order_in.customer_name is not None else None,
        product_description=order_in.product_description.strip() if order_in.product_description is not None else None,
        priority=order_in.priority,
        status=order_in.status,
    )

    if order["priority"] == "High" and old_priority != "High":
        background_tasks.add_task(
            send_email_background,
            order["order_id"],
            order["customer_name"],
            order["product_description"],
        )

    return order


@app.delete("/api/orders/{order_id}", dependencies=[Depends(check_api_key)])
async def delete_order(order_id: int):
    if not database.delete_order(order_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    return {"message": "Đã xóa đơn hàng"}


@app.post("/api/orders/{order_id}/trigger-email", dependencies=[Depends(check_api_key)])
async def trigger_email(order_id: int, background_tasks: BackgroundTasks):
    order = database.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    background_tasks.add_task(
        send_email_background,
        order["order_id"],
        order["customer_name"],
        order["product_description"],
    )
    return {"message": f"Đã gửi yêu cầu soạn email cho đơn #{order_id}"}


@app.get("/api/orders/{order_id}/logs", response_model=List[OrderLogOut], dependencies=[Depends(check_api_key)])
async def get_order_logs(order_id: int):
    return database.list_order_logs(order_id)


@app.get("/api/logs", response_model=List[OrderLogOut], dependencies=[Depends(check_api_key)])
async def get_all_logs():
    return database.list_all_logs(limit=50)
