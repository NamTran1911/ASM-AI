from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String(255), nullable=False)
    product_description = Column(Text, nullable=False)
    priority = Column(String(50), nullable=False, default="Medium")
    status = Column(String(50), nullable=False, default="Pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    logs = relationship("OrderLog", back_populates="order", cascade="all, delete-orphan")


class OrderLog(Base):
    __tablename__ = "order_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), default="AUTO_EMAIL_REPLY")
    recipient = Column(String(255), nullable=True)
    email_subject = Column(String(255), nullable=True)
    email_content = Column(Text, nullable=False)
    status = Column(String(50), default="SENT")
    created_at = Column(DateTime, server_default=func.now())

    order = relationship("Order", back_populates="logs")
