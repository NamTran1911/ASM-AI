from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    customer_name: str
    product_description: str
    priority: Optional[str] = None
    status: str = "Pending"


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    product_description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class PredictRequest(BaseModel):
    product_description: str


class OrderLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: int
    order_id: int
    action: str
    recipient: Optional[str] = None
    email_subject: Optional[str] = None
    email_content: str
    status: str
    created_at: datetime


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    order_id: int
    customer_name: str
    product_description: str
    priority: str
    status: str
    created_at: datetime
