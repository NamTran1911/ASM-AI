import os
import logging
from typing import List, Optional

from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks, Header
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import Base, engine, get_db
from app.models import Order, OrderLog
from app.schemas import OrderCreate, OrderUpdate, OrderOut, OrderLogOut, PredictRequest
from app.ml import predict_priority, model as ml_model
from app.services import send_email_background

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Tạo bảng database tự động nếu chưa có
Base.metadata.create_all(bind=engine)

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
    db: Session = Depends(get_db),
):
    query = db.query(Order)
    if priority:
        query = query.filter(Order.priority == priority)
    if status:
        query = query.filter(Order.status == status)
    if search:
        kw = f"%{search.strip()}%"
        query = query.filter(or_(Order.customer_name.ilike(kw), Order.product_description.ilike(kw)))
    return query.order_by(Order.order_id.desc()).all()


@app.get("/api/orders/{order_id}", response_model=OrderOut, dependencies=[Depends(check_api_key)])
async def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    return order


@app.post("/api/orders", response_model=OrderOut, status_code=201, dependencies=[Depends(check_api_key)])
async def create_order(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Nếu chưa chọn priority thì gọi ML dự đoán tự động
    priority = order_in.priority
    if priority not in ("High", "Medium", "Low"):
        priority = predict_priority(order_in.product_description)["priority"]

    new_order = Order(
        customer_name=order_in.customer_name.strip(),
        product_description=order_in.product_description.strip(),
        priority=priority,
        status=order_in.status or "Pending",
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Đơn High Priority thì chạy background task soạn email
    if new_order.priority == "High":
        background_tasks.add_task(
            send_email_background,
            new_order.order_id,
            new_order.customer_name,
            new_order.product_description,
        )

    return new_order


@app.put("/api/orders/{order_id}", response_model=OrderOut, dependencies=[Depends(check_api_key)])
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    old_priority = order.priority

    if order_in.customer_name is not None:
        order.customer_name = order_in.customer_name.strip()
    if order_in.product_description is not None:
        order.product_description = order_in.product_description.strip()
    if order_in.priority is not None:
        order.priority = order_in.priority
    if order_in.status is not None:
        order.status = order_in.status

    db.commit()
    db.refresh(order)

    if order.priority == "High" and old_priority != "High":
        background_tasks.add_task(
            send_email_background,
            order.order_id,
            order.customer_name,
            order.product_description,
        )

    return order


@app.delete("/api/orders/{order_id}", dependencies=[Depends(check_api_key)])
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")
    db.delete(order)
    db.commit()
    return {"message": "Đã xóa đơn hàng"}


@app.post("/api/orders/{order_id}/trigger-email", dependencies=[Depends(check_api_key)])
async def trigger_email(order_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    background_tasks.add_task(
        send_email_background,
        order.order_id,
        order.customer_name,
        order.product_description,
    )
    return {"message": f"Đã gửi yêu cầu soạn email cho đơn #{order_id}"}


@app.get("/api/orders/{order_id}/logs", response_model=List[OrderLogOut], dependencies=[Depends(check_api_key)])
async def get_order_logs(order_id: int, db: Session = Depends(get_db)):
    return (
        db.query(OrderLog)
        .filter(OrderLog.order_id == order_id)
        .order_by(OrderLog.log_id.desc())
        .all()
    )


@app.get("/api/logs", response_model=List[OrderLogOut], dependencies=[Depends(check_api_key)])
async def get_all_logs(db: Session = Depends(get_db)):
    return db.query(OrderLog).order_by(OrderLog.log_id.desc()).limit(50).all()
