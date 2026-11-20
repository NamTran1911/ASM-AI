from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import Order, OrderLog
from app.schemas import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderLogResponse,
    PredictRequest,
    PredictResponse
)
from app.ml import predict_order_priority
from app.services import background_email_task
from app.auth import verify_api_key

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    # Neu nguoi dung chua chon priority hoac de trong, tu dong du doan bang ML
    priority = order_in.priority
    if not priority or priority not in ["High", "Medium", "Low"]:
        prediction = predict_order_priority(order_in.product_description)
        priority = prediction["priority"]

    new_order = Order(
        customer_name=order_in.customer_name.strip(),
        product_description=order_in.product_description.strip(),
        priority=priority,
        status=order_in.status or "Pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Neu priority la High, kich hoat BackgroundTasks de soan thao email
    if new_order.priority == "High":
        background_tasks.add_task(
            background_email_task,
            new_order.order_id,
            new_order.customer_name,
            new_order.product_description
        )

    return new_order

@router.get("", response_model=List[OrderResponse])
async def list_orders(
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    query = db.query(Order)

    if priority:
        query = query.filter(Order.priority == priority)
    if status_filter:
        query = query.filter(Order.status == status_filter)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Order.customer_name.ilike(search_pattern),
                Order.product_description.ilike(search_pattern)
            )
        )

    orders = query.order_by(Order.order_id.desc()).offset(offset).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Khong tim thay don hang #{order_id}"
        )
    return order

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Khong tim thay don hang #{order_id}"
        )

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

    # Neu don hang cap nhat len High tu muc khac thi kich hoat background task
    if order.priority == "High" and old_priority != "High":
        background_tasks.add_task(
            background_email_task,
            order.order_id,
            order.customer_name,
            order.product_description
        )

    return order

@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Khong tim thay don hang #{order_id}"
        )

    db.delete(order)
    db.commit()
    return {"message": "Da xoa don hang thanh cong", "order_id": order_id}

@router.post("/predict", response_model=PredictResponse)
async def predict_priority(
    payload: PredictRequest,
    _auth: Optional[str] = Depends(verify_api_key)
):
    result = predict_order_priority(payload.product_description)
    return result

@router.post("/{order_id}/trigger-email")
async def trigger_email_manually(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Khong tim thay don hang #{order_id}"
        )

    background_tasks.add_task(
        background_email_task,
        order.order_id,
        order.customer_name,
        order.product_description
    )
    return {"message": f"Da them tac vu gui email vao background task cho don hang #{order_id}"}

@router.get("/{order_id}/logs", response_model=List[OrderLogResponse])
async def get_order_logs(
    order_id: int,
    db: Session = Depends(get_db),
    _auth: Optional[str] = Depends(verify_api_key)
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Khong tim thay don hang #{order_id}"
        )
    logs = db.query(OrderLog).filter(OrderLog.order_id == order_id).order_by(OrderLog.log_id.desc()).all()
    return logs
