"""Payment SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class PaymentModel(Base):
    """Payment database model."""
    
    __tablename__ = "payments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # в копейках
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    provider: Mapped[str] = mapped_column(String(20), nullable=False, default="yookassa")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payment_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order: Mapped["OrderModel"] = relationship("OrderModel", back_populates="payment")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="payments")
    
    def __repr__(self) -> str:
        return f"<PaymentModel(id={self.id}, order_id={self.order_id}, amount={self.amount}, status={self.status})>"