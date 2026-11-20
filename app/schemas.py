from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=255)
    product_description: str = Field(..., min_length=1)
    priority: Optional[str] = Field(default="Medium")
    status: Optional[str] = Field(default="Pending")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    product_description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class OrderLogResponse(BaseModel):
    log_id: int
    order_id: int
    action: str
    recipient: Optional[str] = None
    email_subject: Optional[str] = None
    email_content: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class OrderResponse(OrderBase):
    order_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    logs: List[OrderLogResponse] = []

    class Config:
        from_attributes = True

class PredictRequest(BaseModel):
    product_description: str = Field(..., min_length=1)

class PredictResponse(BaseModel):
    priority: str
    confidence: float
    description_cleaned: str
