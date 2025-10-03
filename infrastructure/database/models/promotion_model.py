"""Promotion SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from infrastructure.database.connection import Base


class PromotionModel(Base):
    """Promotion database model."""
    
    __tablename__ = "promotions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Promotion type: percentage, fixed_amount, free_delivery
    promotion_type: Mapped[str] = mapped_column(String(20), nullable=False, default="percentage")
    discount_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # процент или копейки
    
    # Conditions
    min_order_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # в копейках
    max_discount_amount: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # в копейках
    usage_limit: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # максимальное количество использований
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # количество использований
    
    # Validity
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    usages: Mapped[list["PromotionUsageModel"]] = relationship("PromotionUsageModel", back_populates="promotion")
    
    def __repr__(self) -> str:
        return f"<PromotionModel(id={self.id}, code={self.code}, type={self.promotion_type})>"


class PromotionUsageModel(Base):
    """Promotion usage database model."""
    
    __tablename__ = "promotion_usages"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    promotion_id: Mapped[str] = mapped_column(String(36), ForeignKey("promotions.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), nullable=False)
    discount_amount: Mapped[int] = mapped_column(Integer, nullable=False)  # в копейках
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    promotion: Mapped["PromotionModel"] = relationship("PromotionModel", back_populates="usages")
    user: Mapped["UserModel"] = relationship("UserModel")
    order: Mapped["OrderModel"] = relationship("OrderModel")
    
    def __repr__(self) -> str:
        return f"<PromotionUsageModel(id={self.id}, promotion_id={self.promotion_id}, user_id={self.user_id})>"