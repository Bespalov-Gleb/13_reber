"""User SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class UserModel(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="customer")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="ru")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="Europe/Moscow")
    is_notifications_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_spent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # в копейках
    last_order_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    carts: Mapped[list["CartModel"]] = relationship("CartModel", back_populates="user")
    orders: Mapped[list["OrderModel"]] = relationship("OrderModel", back_populates="user")
    payments: Mapped[list["PaymentModel"]] = relationship("PaymentModel", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"