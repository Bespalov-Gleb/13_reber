"""Order SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class OrderModel(Base):
    """Order database model."""
    
    __tablename__ = "orders"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)  # delivery, pickup
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False, default="cash")
    payment_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    
    # Order details
    items: Mapped[dict] = mapped_column(JSON, nullable=False)  # Список товаров с количеством и ценой
    subtotal: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # в копейках
    delivery_fee: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # в копейках
    discount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # в копейках
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # в копейках
    
    # Delivery/Pickup info
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    delivery_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivery_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Order comment
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    preparing_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ready_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="orders")
    payment: Mapped[Optional["PaymentModel"]] = relationship("PaymentModel", back_populates="order", uselist=False)
    
    def __repr__(self) -> str:
        return f"<OrderModel(id={self.id}, user_id={self.user_id}, status={self.status}, total={self.total})>"